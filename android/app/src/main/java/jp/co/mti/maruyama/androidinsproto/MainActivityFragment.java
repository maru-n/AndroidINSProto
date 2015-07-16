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
import android.widget.CompoundButton;
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

    private Switch mSensorSerialSwitch;
    private TextView mAccelValueTextView;
    private TextView mGyroValueTextView;
    private TextView mMagValueTextView;

    private float accelValue[] = new float[3];
    private float gyroValue[] = new float[3];
    private float magValue[] = new float[3];

    private PendingIntent mPermissionIntent;
    private static final String ACTION_USB_PERMISSION = "jp.co.mti.maruyama.androidinsproto.USB_PERMISSION";

    private static final byte SERIAL_REQUEST_CODE_ALL_SENSOR_DATA = 1;
    private static final byte SERIAL_REQUEST_CODE_ACCEL_SENSOR_DATA = 2;
    private static final byte SERIAL_REQUEST_CODE_GYRO_SENSOR_DATA = 3;
    private static final byte SERIAL_REQUEST_CODE_MAG_SENSOR_DATA = 4;

    private final BroadcastReceiver mUsbReceiver = new BroadcastReceiver() {

        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (ACTION_USB_PERMISSION.equals(action)) {
                synchronized (this) {
                    UsbDevice device = (UsbDevice)intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);

                    if (intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false)) {
                        if(device != null){
                            MainActivityFragment.this.openSerialIOPort(device);
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

        mSensorSerialSwitch = (Switch)view.findViewById(R.id.sensor_serial_switch);
        mSensorSerialSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    setupSensor();
                    setupUsbSerialIO();
                } else {
                    stopSensor();
                    stopUsbSerialIo();
                }
            }
        });

        mAccelValueTextView = (TextView)view.findViewById(R.id.accel_value_text);
        mGyroValueTextView = (TextView)view.findViewById(R.id.gyro_value_text);
        mMagValueTextView = (TextView)view.findViewById(R.id.mag_value_text);

        mPermissionIntent = PendingIntent.getBroadcast(this.getActivity(), 0, new Intent(ACTION_USB_PERMISSION), 0);
        IntentFilter filter = new IntentFilter(ACTION_USB_PERMISSION);
        this.getActivity().registerReceiver(mUsbReceiver, filter);
        setupUsbSerialIO();
        return view;
    }

    @Override
    public void onResume() {
        super.onResume();
        setupSensor();
        if (mSerialIoManager == null) {
            setupUsbSerialIO();
        }
    }

    private void setupSensor() {

        Activity activity = this.getActivity();
        mSensorManager = (SensorManager)activity.getSystemService(Activity.SENSOR_SERVICE);

        List<Sensor> sensors = mSensorManager.getSensorList(Sensor.TYPE_ALL);
        /*
        Log.d(TAG, "Sensor list");
        for(Sensor s: sensors){
            Log.d(TAG, s.getName());
        }
        */

        if (mSensorManager != null) {
            List<Sensor> accelSensors = mSensorManager.getSensorList(Sensor.TYPE_ACCELEROMETER);
            if (accelSensors.size() < 1) {
                Log.w(TAG, "Accelerometer is not available.");
            } else {
                mSensorManager.registerListener(this, accelSensors.get(0), SensorManager.SENSOR_DELAY_FASTEST);
            }
            List<Sensor> gyroSensors = mSensorManager.getSensorList(Sensor.TYPE_GYROSCOPE);
            if (gyroSensors.size() < 1) {
                Log.w(TAG, "Gyroscope is not available.");
            } else {
                mSensorManager.registerListener(this, gyroSensors.get(0), SensorManager.SENSOR_DELAY_FASTEST);
            }
            List<Sensor> magSensors = mSensorManager.getSensorList(Sensor.TYPE_MAGNETIC_FIELD);
            if (magSensors.size() < 1) {
                Log.w(TAG, "Magnetic field sensor is not available.");
            } else {
                mSensorManager.registerListener(this, magSensors.get(0), SensorManager.SENSOR_DELAY_FASTEST);
            }
        }
    }

    private void stopSensor() {
        if (mSensorManager != null) {
            mSensorManager.unregisterListener(this);
        }
    }

    private void setupUsbSerialIO() {
        //stopSerialIo();

        final UsbManager usbManager = (UsbManager) this.getActivity().getSystemService(this.getActivity().USB_SERVICE);

        List<UsbSerialDriver> availableDrivers = UsbSerialProber.getDefaultProber().findAllDrivers(usbManager);
        if (availableDrivers.isEmpty()) {
            Log.w(TAG, "no available drivers.");
            return;
        }
        UsbSerialDriver driver = availableDrivers.get(0);
        UsbSerialPort port = driver.getPorts().get(0);
        UsbDevice device = port.getDriver().getDevice();
        if (usbManager.hasPermission(device)) {
            openSerialIOPort(device);
        }else {
            usbManager.requestPermission(port.getDriver().getDevice(), mPermissionIntent);
        }
    }

    private void openSerialIOPort(UsbDevice device) {

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
                Log.d(TAG, "test");
                for (int i=0; i<data.length; i++) {
                    switch (data[i]) {
                        case SERIAL_REQUEST_CODE_ALL_SENSOR_DATA:
                            sendSensorValue(accelValue);
                            sendSensorValue(gyroValue);
                            sendSensorValue(magValue);
                            break;
                        case SERIAL_REQUEST_CODE_ACCEL_SENSOR_DATA:
                            sendSensorValue(accelValue);
                            break;
                        case SERIAL_REQUEST_CODE_GYRO_SENSOR_DATA:
                            sendSensorValue(gyroValue);
                            break;
                        case SERIAL_REQUEST_CODE_MAG_SENSOR_DATA:
                            sendSensorValue(magValue);
                            break;
                        default:
                            break;
                    }
                }
                /*
                final String msg = "Read: " + HexDump.toHexString(data) + "|" + new String(data) + " (" + data.length + "bytes)";
                Log.i(TAG, msg);
                */
            }
        });
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.submit(mSerialIoManager);
    }

    private void sendSensorValue(float[] val) {
        ByteBuffer buf = ByteBuffer.allocate(Float.SIZE * 3 / Byte.SIZE);
        buf.putFloat(val[0]);
        buf.putFloat(val[1]);
        buf.putFloat(val[2]);
        byte[] data = buf.array();
        writeSerial(data);

    }

    private void stopUsbSerialIo() {
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
        switch (event.sensor.getType()) {
            case Sensor.TYPE_ACCELEROMETER:
                for (int i = 0; i < 3; i++) {
                    accelValue[i] = event.values[i];
                }
                break;
            case Sensor.TYPE_GYROSCOPE:
                for (int i = 0; i < 3; i++) {
                    gyroValue[i] = event.values[i];
                }
                break;
            case Sensor.TYPE_MAGNETIC_FIELD:
                for (int i = 0; i < 3; i++) {
                    magValue[i] = event.values[i];
                }
                break;
        }
        setSensorDataText();
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        Log.i(TAG, "sensor accuracy: " + accuracy);
    }

    private void setSensorDataText() {
        String s;
        s = String.format("x:%.3f y:%.3f z:%.3f", accelValue[0], accelValue[1], accelValue[2]);
        mAccelValueTextView.setText(s);
        s = String.format("x:%.3f y:%.3f z:%.3f", gyroValue[0], gyroValue[1], gyroValue[2]);
        mGyroValueTextView.setText(s);
        s = String.format("x:%.3f y:%.3f z:%.3f", magValue[0], magValue[1], magValue[2]);
        mMagValueTextView.setText(s);
    }
}
