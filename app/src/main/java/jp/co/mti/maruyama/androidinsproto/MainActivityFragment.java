package jp.co.mti.maruyama.androidinsproto;

import android.app.Activity;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorManager;
import android.hardware.SensorEventListener;
import android.hardware.usb.UsbManager;
import android.support.v4.app.Fragment;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

//import com.hoho.android.usbserial.driver.*;

import java.util.List;


/**
 * A placeholder fragment containing a simple view.
 */
public class MainActivityFragment extends Fragment implements SensorEventListener {

    private SensorManager mSensorManager;

    public MainActivityFragment() {
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {


        Activity activity = this.getActivity();
        mSensorManager = (SensorManager)activity.getSystemService(Activity.SENSOR_SERVICE);

        List<Sensor> sensors = mSensorManager.getSensorList(Sensor.TYPE_ALL);
        for(Sensor s: sensors){
            Log.d(this.toString(), s.getName());
        }
        /*
        UsbManager usbManager = (UsbManager)activity.getSystemService(activity.USB_SERVICE);

        List<UsbSerialDriver> availableDrivers = UsbSerialProber.getDefaultProber().findAllDrivers(manager);
        if (availableDrivers.isEmpty()) {
            return;
        }

        // Open a connection to the first available driver.
        UsbSerialDriver driver = availableDrivers.get(0);
        UsbDeviceConnection connection = manager.openDevice(driver.getDevice());
        if (connection == null) {
            // You probably need to call UsbManager.requestPermission(driver.getDevice(), ..)
            return;
        }

        // Read some data! Most have just one port (port 0).
        UsbSerialPort port = driver.getPort(0);
        port.open(connection);
        try {
            port.setBaudRate(115200);
            byte buffer[] = new byte[16];
            int numBytesRead = port.read(buffer, 1000);
            Log.d(TAG, "Read " + numBytesRead + " bytes.");
        } catch (IOException e) {
            // Deal with error.
        } finally {
            port.close();
        }
        */

        return inflater.inflate(R.layout.fragment_main, container, false);
    }

    @Override
    public void onResume() {
        super.onResume();
        if (mSensorManager != null) {
            List<Sensor> accelSensors = mSensorManager.getSensorList(Sensor.TYPE_ACCELEROMETER);
            if (accelSensors.size() > 0) {
                Sensor s = accelSensors.get(0);
                mSensorManager.registerListener(this, s, SensorManager.SENSOR_DELAY_FASTEST);
            }
        }
    }

    @Override
    public void onPause() {
        super.onPause();
        if (mSensorManager != null) {
            mSensorManager.unregisterListener(this);
        }
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        Log.d(this.toString(), "x:"+event.values[0]+" y:"+event.values[1]+" z:"+event.values[2]);
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        Log.d(this.toString(), "accuracy:" + accuracy);
    }
}
