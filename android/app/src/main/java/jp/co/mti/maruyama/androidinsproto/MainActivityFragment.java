package jp.co.mti.maruyama.androidinsproto;

import android.app.Activity;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorManager;
import android.hardware.SensorEventListener;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbManager;
import android.hardware.usb.UsbDeviceConnection;
import android.support.v4.app.Fragment;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.Switch;
import android.widget.TextView;

import com.hoho.android.usbserial.driver.UsbSerialPort;
import com.hoho.android.usbserial.driver.UsbSerialDriver;
import com.hoho.android.usbserial.driver.UsbSerialProber;
import com.hoho.android.usbserial.util.SerialInputOutputManager;
import com.hoho.android.usbserial.util.HexDump;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import java.io.IOException;
import java.util.List;
import java.nio.ByteBuffer;


/**
 * A placeholder fragment containing a simple view.
 */
public class MainActivityFragment extends Fragment implements SensorEventListener {

    private final String TAG = this.getClass().getSimpleName();

    private SensorManager mSensorManager;
    private SerialInputOutputManager mSerialIoManager;

    private Switch mSerialSwitch;
    private TextView mAccelerationValueTextView;

    private PendingIntent mPermissionIntent;
    private static final String ACTION_USB_PERMISSION = "jp.co.mti.maruyama.androidinsproto.USB_PERMISSION";

    private final BroadcastReceiver mUsbReceiver = new BroadcastReceiver() {

        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (ACTION_USB_PERMISSION.equals(action)) {
                synchronized (this) {
                    UsbDevice device = (UsbDevice)intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);

                    if (intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false)) {
                        if(device != null){
                            MainActivityFragment.this.openSerialIO(device);
                        }
                    }
                    else {
                        Log.d(TAG, "permission denied for device " + device);
                    }
                }
            }
        }
    };

    public MainActivityFragment() {}

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_main, container, false);
        Button button = (Button)view.findViewById(R.id.serial_test_button);
        button.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {
                String msg = "test";
                writeSerial(msg);
            }
        });
        mSerialSwitch = (Switch)view.findViewById(R.id.serial_switch);
        mAccelerationValueTextView = (TextView)view.findViewById(R.id.acceleration_value_text);

        mPermissionIntent = PendingIntent.getBroadcast(this.getActivity(), 0, new Intent(ACTION_USB_PERMISSION), 0);
        IntentFilter filter = new IntentFilter(ACTION_USB_PERMISSION);
        this.getActivity().registerReceiver(mUsbReceiver, filter);
        setupUsbSerial();
        return view;
    }

    @Override
    public void onResume() {
        super.onResume();
        setupSensor();
    }

    @Override
    public void onPause() {
        super.onPause();
        if (mSensorManager != null) {
            mSensorManager.unregisterListener(this);
        }
        closeSerialIo();
    }

    private void setupSensor() {
        Activity activity = this.getActivity();
        mSensorManager = (SensorManager)activity.getSystemService(Activity.SENSOR_SERVICE);

        List<Sensor> sensors = mSensorManager.getSensorList(Sensor.TYPE_ALL);

        Log.d(TAG, "Sensor list");
        for(Sensor s: sensors){
            Log.d(TAG, s.getName());
        }

        if (mSensorManager != null) {
            List<Sensor> accelSensors = mSensorManager.getSensorList(Sensor.TYPE_ACCELEROMETER);
            if (accelSensors.size() > 0) {
                Sensor s = accelSensors.get(0);
                mSensorManager.registerListener(this, s, SensorManager.SENSOR_DELAY_FASTEST);
            }
        }
    }

    private void setupUsbSerial() {
        //stopSerialIo();

        final UsbManager usbManager = (UsbManager) this.getActivity().getSystemService(this.getActivity().USB_SERVICE);

        List<UsbSerialDriver> availableDrivers = UsbSerialProber.getDefaultProber().findAllDrivers(usbManager);
        if (availableDrivers.isEmpty()) {
            Log.w(TAG, "no available drivers.");
            return;
        }
        UsbSerialDriver driver = availableDrivers.get(0);
        UsbSerialPort port = driver.getPorts().get(0);

        usbManager.requestPermission(port.getDriver().getDevice(), mPermissionIntent);
    }

    private void openSerialIO(UsbDevice device) {

        UsbSerialDriver driver = UsbSerialProber.getDefaultProber().probeDevice(device);
        UsbSerialPort port = driver.getPorts().get(0);

        Activity activity = MainActivityFragment.this.getActivity();
        final UsbManager usbManager = (UsbManager)activity.getSystemService(activity.USB_SERVICE);
        UsbDeviceConnection connection = usbManager.openDevice(port.getDriver().getDevice());
        if (connection == null) {
            Log.d(TAG, "Opening device failed");
            return;
        }

        try {
            port.open(connection);
            port.setParameters(115200, 8, UsbSerialPort.STOPBITS_1, UsbSerialPort.PARITY_NONE);
        } catch (IOException e) {
            Log.e(TAG, "Error setting up device: " + e.getMessage(), e);
            Log.d(TAG, "Error opening device: " + e.getMessage());
            try {
                port.close();
            } catch (IOException e2) {
                // Ignore.
            }
            return;
        }
        Log.d(TAG, "Serial device: " + port.getClass().getSimpleName());

        mSerialIoManager = new SerialInputOutputManager(port, new SerialInputOutputManager.Listener() {
            @Override
            public void onRunError(Exception e) {
                Log.d(TAG, "Runner stopped.");
            }
            @Override
            public void onNewData(final byte[] data) {
                final String msg = "Read: " + HexDump.toHexString(data) + "|" + new String(data) + " (" + data.length + "bytes)";
                Log.i(TAG, msg);
            }
        });
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.submit(mSerialIoManager);
    }

    private void closeSerialIo() {
        if (mSerialIoManager != null) {
            Log.i(TAG, "Stopping serial IO.");
            mSerialIoManager.stop();
            mSerialIoManager = null;
        }
    }

    private void writeSerial(String msg) {
        byte[] data = msg.getBytes();
        writeSerial(data);
    }

    private void writeSerial(byte[] data) {
        if (mSerialIoManager == null) {
            Log.w(TAG, "Serial IO is not available.");
            return;
        }
        mSerialIoManager.writeAsync(data);
    }


    /*
     * SensorEventListener
     */
    @Override
    public void onSensorChanged(SensorEvent event) {
        String s = String.format("x:%.3f y:%.3f z:%.3f", event.values[0], event.values[1], event.values[2]);
        mAccelerationValueTextView.setText(s);

        if (mSerialSwitch.isChecked()) {
            ByteBuffer buf = ByteBuffer.allocate(Float.SIZE * 3 / Byte.SIZE);
            buf.putFloat(event.values[0]);
            buf.putFloat(event.values[1]);
            buf.putFloat(event.values[2]);
            byte[] data = buf.array();
            writeSerial(data);
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        Log.i(TAG, "sensor accuracy: " + accuracy);
    }
}
