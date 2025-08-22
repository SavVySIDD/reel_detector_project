package com.example.reeldetector

data class PacketMeta(val ts: Double, val length: Int, val src: String, val dst: String)

class FeatureBuffer(val deviceIp: String, val windowSize: Double = 5.0, val step: Double = 2.5) {
    private val buffer = mutableListOf<PacketMeta>()

    fun addPacket(pm: PacketMeta) {
        buffer.add(pm)
        val cutoff = pm.ts - 10.0*windowSize
        while (buffer.isNotEmpty() && buffer[0].ts < cutoff) buffer.removeAt(0)
    }

    fun computeLatestWindow(): FloatArray? {
        if (buffer.isEmpty()) return null
        val end = buffer.last().ts
        val start = end - windowSize
        val window = buffer.filter { it.ts >= start }
        if (window.isEmpty()) return null
        val down = window.filter { it.dst == deviceIp }.map { it.length.toDouble() }.toDoubleArray()
        val up = window.filter { it.src == deviceIp }.map { it.length.toDouble() }.toDoubleArray()
        val bd = if (down.isEmpty()) 0.0 else down.sum()
        val nd = down.size.toDouble()
        val bu = if (up.isEmpty()) 0.0 else up.sum()
        val nu = up.size.toDouble()
        val bitrate = bd / windowSize
        val iat_mean = if (down.size > 1) {
            val ts = window.filter { it.dst == deviceIp }.map { it.ts }
            ts.zipWithNext { a,b -> b - a }.average()
        } else 0.0
        val burst_count = down.count { it > 1000.0 }
        val ratio = bd / (bu + 1.0)
        return floatArrayOf(
            bd.toFloat(), nd.toFloat(), (if (nd>0) (bd/nd).toFloat() else 0f), 0f,
            bu.toFloat(), nu.toFloat(), (if (nu>0) (bu/nu).toFloat() else 0f), 0f,
            bitrate.toFloat(), iat_mean.toFloat(), 0f, burst_count.toFloat(), ratio.toFloat()
        )
    }
}
