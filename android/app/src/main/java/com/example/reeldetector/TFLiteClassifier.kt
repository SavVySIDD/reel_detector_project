package com.example.reeldetector

import android.content.res.AssetFileDescriptor
import android.content.res.AssetManager
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.system.measureNanoTime

class TFLiteClassifier(am: AssetManager, modelPath: String) {
    private val interpreter: Interpreter = Interpreter(loadModelFile(am, modelPath))

    private fun loadModelFile(am: AssetManager, path: String): MappedByteBuffer {
        val afd: AssetFileDescriptor = am.openFd(path)
        val fis = FileInputStream(afd.fileDescriptor)
        val fc = fis.channel
        val bb = fc.map(FileChannel.MapMode.READ_ONLY, afd.startOffset, afd.length)
        fis.close()
        return bb
    }

    fun predictNormalized(input: FloatArray): Float {
        val byteBuffer = ByteBuffer.allocateDirect(input.size * 4).order(ByteOrder.nativeOrder())
        input.forEach { byteBuffer.putFloat(it) }
        byteBuffer.rewind()
        val output = Array(1) { FloatArray(1) }
        val timeNs = measureNanoTime {
            interpreter.run(byteBuffer, output)
        }
        // inference time in ms: timeNs / 1e6
        return output[0][0]
    }
}
