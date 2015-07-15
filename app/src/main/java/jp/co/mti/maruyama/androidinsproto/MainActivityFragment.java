package jp.co.mti.maruyama.androidinsproto;

import android.app.Activity;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorManager;
import android.hardware.SensorEventListener;
import android.hardware.usb.UsbManager;
import android.hardware.usb.UsbDeviceConnection;
import android.support.v4.app.Fragment;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import com.hoho.android.usbserial.driver.UsbSerialPort;
import com.hoho.android.usbserial.driver.UsbSerialDriver;
import com.hoho.android.usbserial.driver.UsbSerialProber;
import com.hoho.android.usbserial.util.SerialInputOutputManager;
import com.hoho.android.usbserial.util.HexDump;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import java.io.IOException;
import java.util.List;


/**
 * A placeholder fragment containing a simple view.
 */
public class MainActivityFragment extends Fragment implements SensorEventListener {

    private final String LOG_TAG = this.getClass().getSimpleName();

    private SensorManager mSensorManager;
    private SerialInputOutputManager mSerialIoManager;

    private static UsbSerialPort mSerialPort = null;
    private final ExecutorService mExecutor = Executors.newSingleThreadExecutor();

    private final SerialInputOutputManager.Listener mSerialIOListener = new SerialInputOutputManager.Listener() {
        @Override
        public void onRunError(Exception e) {
            Log.d(LOG_TAG, "Runner stopped.");
        }

        @Override
        public void onNewData(final byte[] data) {
            final String msg = "Read: " + HexDump.toHexString(data) + "|" + new String(data) + " (" + data.length + "bytes)";
            Log.i(LOG_TAG, msg);
        }
    };

    private final View.OnClickListener mOnClickTestButtonListener = new View.OnClickListener(){
        @Override
        public void onClick(View v) {
            String msg = "test";
            writeSerial(msg);
        }
    };

    public MainActivityFragment() {}

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_main, container, false);
        Button button = (Button)view.findViewById(R.id.test_button);
        button.setOnClickListener(mOnClickTestButtonListener);
        return view;
    }

    @Override
    public void onResume() {
        super.onResume();
        setupSensor();
        setupSerialIO();
        Log.d(LOG_TAG, "Resumed, port=" + mSerialPort);
    }

    @Override
    public void onPause() {
        super.onPause();
        if (mSensorManager != null) {
            mSensorManager.unregisterListener(this);
        }

        stopIoManager();
        if (mSerialPort != null) {
            try {
                mSerialPort.close();
            } catch (IOException e) {
                // Ignore.
            }
            mSerialPort = null;
        }
        this.getActivity().finish();
    }

    private void setupSensor() {
        Activity activity = this.getActivity();
        mSensorManager = (SensorManager)activity.getSystemService(Activity.SENSOR_SERVICE);

        List<Sensor> sensors = mSensorManager.getSensorList(Sensor.TYPE_ALL);
        Log.d(LOG_TAG, "Sensor list");
        for(Sensor s: sensors){
            Log.d(LOG_TAG, s.getName());
        }

        if (mSensorManager != null) {
            List<Sensor> accelSensors = mSensorManager.getSensorList(Sensor.TYPE_ACCELEROMETER);
            if (accelSensors.size() > 0) {
                Sensor s = accelSensors.get(0);
                mSensorManager.registerListener(this, s, SensorManager.SENSOR_DELAY_FASTEST);
            }
        }
    }

    private void setupSerialIO() {
        final UsbManager usbManager = (UsbManager)this.getActivity().getSystemService(this.getActivity().USB_SERVICE);

        if (mSerialPort == null) {

            Log.d(LOG_TAG, "setupUsbSerial");

            List<UsbSerialDriver> availableDrivers =
                    UsbSerialProber.getDefaultProber().findAllDrivers(usbManager);
            if (availableDrivers.isEmpty()) {
                Log.w(LOG_TAG, "no available drivers.");
                return;
            }

            UsbSerialDriver driver = availableDrivers.get(0);
            UsbDeviceConnection connection = usbManager.openDevice(driver.getDevice());
            if (connection == null) {
                Log.w(LOG_TAG, "unable to open the connection.");
                // You probably need to call UsbManager.requestPermission(driver.getDevice(), ..)
                return;
            }

            List<UsbSerialPort> ports = driver.getPorts();
            for(UsbSerialPort p: ports){
                Log.d(LOG_TAG, p.toString());
            }
            mSerialPort = ports.get(0);

        }

        UsbDeviceConnection connection = usbManager.openDevice(mSerialPort.getDriver().getDevice());
        if (connection == null) {
            Log.d(LOG_TAG, "Opening device failed");
            return;
        }

        try {
            mSerialPort.open(connection);
            mSerialPort.setParameters(115200, 8, UsbSerialPort.STOPBITS_1, UsbSerialPort.PARITY_NONE);
        } catch (IOException e) {
            Log.e(LOG_TAG, "Error setting up device: " + e.getMessage(), e);
            Log.d(LOG_TAG, "Error opening device: " + e.getMessage());
            try {
                mSerialPort.close();
            } catch (IOException e2) {
                // Ignore.
            }
            mSerialPort = null;
            return;
        }
        Log.d(LOG_TAG, "Serial device: " + mSerialPort.getClass().getSimpleName());
        onDeviceStateChange();
    }

    private void onDeviceStateChange() {
        stopIoManager();
        startIoManager();
    }

    private void stopIoManager() {
        if (mSerialIoManager != null) {
            Log.i(LOG_TAG, "Stopping serial io manager ..");
            mSerialIoManager.stop();
            mSerialIoManager = null;
        }
    }

    private void startIoManager() {
        if (mSerialPort != null) {
            Log.i(LOG_TAG, "Starting serial io manager ..");
            mSerialIoManager = new SerialInputOutputManager(mSerialPort, mSerialIOListener);
            mExecutor.submit(mSerialIoManager);
        }
    }

    private void writeSerial(String msg) {
        byte[] data = msg.getBytes();
        writeSerial(data);
    }

    private void writeSerial(byte[] data) {
        try {
            mSerialPort.write(data, data.length);
        } catch (IOException e) {
            Log.w(LOG_TAG, "Serial IO is not available.");
        }
    }

    /*
     * SensorEventListener
     */

    @Override
    public void onSensorChanged(SensorEvent event) {
        String msg = "x:"+event.values[0]+" y:"+event.values[1]+" z:"+event.values[2];
        writeSerial(msg);
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        Log.i(LOG_TAG, "sensor accuracy: " + accuracy);
    }
}
