import CoreImage
import Foundation
import os

/// No laboratório o registro vai para um texto que volta junto com as imagens.
enum LabLog {
    static var lines: [String] = []
    static let lock = NSLock()
}

func dlog(_ message: String) {
    LabLog.lock.lock()
    LabLog.lines.append(message)
    LabLog.lock.unlock()
    print("[revela] " + message)
}

/// O mínimo do Diagnostics do app que a revelação usa.
enum Diagnostics {
    static func ms(since t0: CFAbsoluteTime) -> String {
        String(format: "%.0f ms", (CFAbsoluteTimeGetCurrent() - t0) * 1000)
    }
    static var freeMemory: String {
        String(format: "%.0f MB", Double(os_proc_available_memory()) / 1_048_576)
    }
}
