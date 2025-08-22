package com.example.reeldetector

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import com.google.gson.Gson
import java.io.InputStreamReader

class MainActivity : Activity() {
    lateinit var featureBuffer: FeatureBuffer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val btnStart = findViewById<Button>(R.id.btnStart)
        val btnLabelStart = findViewById<Button>(R.id.btnLabelStart)
        val btnLabelEnd = findViewById<Button>(R.id.btnLabelEnd)
        val tvStatus = findViewById<TextView>(R.id.tvStatus)

        btnStart.setOnClickListener {
            val intent = Intent(this, CaptureVpnService::class.java)
            startService(intent)
            tvStatus.text = "Capture started"
        }

        btnLabelStart.setOnClickListener {
            val intent = Intent(this, CaptureVpnService::class.java)
            intent.action = "LABEL_START"
            startService(intent)
            tvStatus.text = "Label REEL started"
        }

        btnLabelEnd.setOnClickListener {
            val intent = Intent(this, CaptureVpnService::class.java)
            intent.action = "LABEL_END"
            startService(intent)
            tvStatus.text = "Label ended"
        }
    }
}
