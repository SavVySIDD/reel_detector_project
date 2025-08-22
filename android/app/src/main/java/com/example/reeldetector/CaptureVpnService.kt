package com.example.reeldetector

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Intent
import android.net.VpnService
import android.os.Build
import android.os.ParcelFileDescriptor
import android.util.Log
import java.io.File
import java.io.FileOutputStream
import java.io.FileInputStream
import java.net.InetAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.concurrent.thread

class CaptureVpnService : VpnService() {
    private var vpnInterface: ParcelFileDescriptor? = null
    private val deviceIp = "10.0.0.2"
    private val TAG = "CaptureVpnService"
    private lateinit var outFile: File

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundNotification()
        if (vpnInterface == null) {
            setupVpn()
            startCaptureLoop()
        }
        intent?.action?.let {
            if (it == "LABEL_START") writeLabel("LABEL_START")
            if (it == "LABEL_END") writeLabel("LABEL_END")
        }
        return START_STICKY
    }

    private fun startForegroundNotification() {
        val chanId = "reel_channel"
        val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(chanId, "Reel Detector", NotificationManager.IMPORTANCE_LOW)
            nm.createNotificationChannel(channel)
        }
        val not = Notification.Builder(this, chanId)
            .setContentTitle("Reel Detector")
            .setContentText("Capturing metadata")
            .build()
        startForeground(101, not)
    }

    private fun setupVpn() {
        val builder = Builder()
        builder.addAddress(deviceIp, 32)
        builder.addRoute("0.0.0.0", 0)
        builder.setSession("ReelVpn")
        builder.setMtu(1400)
        vpnInterface = builder.establish()
        outFile = File(filesDir, "capture.csv")
        if (!outFile.exists()) {
            outFile.writeText("ts,length,src,dst\n")
        }
        Log.i(TAG, "VPN established, writing to ${outFile.absolutePath}")
    }

    private fun startCaptureLoop() {
        val pfd = vpnInterface ?: return
        val input = FileInputStream(pfd.fileDescriptor)
        val fout = FileOutputStream(File(filesDir, "capture.csv"), true)
        thread(start = true) {
            try {
                val buffer = ByteArray(32768)
                while (true) {
                    val read = input.read(buffer)
                    if (read > 0) {
                        val ts = System.currentTimeMillis().toDouble()/1000.0
                        try {
                            val bb = ByteBuffer.wrap(buffer, 0, read).order(ByteOrder.BIG_ENDIAN)
                            val verIhl = bb.get(0).toInt()
                            val ver = (verIhl shr 4) and 0xF
                            if (ver == 4) {
                                val ihl = (verIhl and 0xF) * 4
                                val srcBytes = ByteArray(4)
                                val dstBytes = ByteArray(4)
                                bb.position(12)
                                bb.get(srcBytes); bb.get(dstBytes)
                                val srcIp = InetAddress.getByAddress(srcBytes).hostAddress
                                val dstIp = InetAddress.getByAddress(dstBytes).hostAddress
                                val line = String.format("%.6f,%d,%s,%s\n", ts, read, srcIp, dstIp)
                                fout.write(line.toByteArray())
                                fout.flush()
                            }
                        } catch (e: Exception) {
                            // ignore
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "capture loop ended: ${e.message}")
            } finally {
                fout.close()
            }
        }
    }

    private fun writeLabel(event: String) {
        val ts = System.currentTimeMillis().toDouble()/1000.0
        val f = File(filesDir, "capture.csv")
        f.appendText("#EVENT,$event,$ts\n")
    }

    override fun onDestroy() {
        vpnInterface?.close()
        super.onDestroy()
    }
}
