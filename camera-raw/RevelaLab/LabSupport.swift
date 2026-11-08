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

/// Memória do processo de teste: phys_footprint (o número que o iOS usa para matar o app por memória).
/// No simulador o os_proc_available_memory devolve ~0 e não serve; o phys_footprint vale.
enum LabMemory {
    static func footprint() -> UInt64 {
        var info = task_vm_info_data_t()
        var count = mach_msg_type_number_t(MemoryLayout<task_vm_info_data_t>.size / MemoryLayout<natural_t>.size)
        let result = withUnsafeMutablePointer(to: &info) { pointer -> kern_return_t in
            pointer.withMemoryRebound(to: integer_t.self, capacity: Int(count)) { raw -> kern_return_t in
                task_info(mach_task_self_, task_flavor_t(TASK_VM_INFO), raw, &count)
            }
        }
        return result == KERN_SUCCESS ? UInt64(info.phys_footprint) : 0
    }
}

/// Pico de memória enquanto um trecho roda: amostra o phys_footprint a cada 20 ms numa fila à parte.
/// (O pico da vida toda do processo não serve: os testes de antes já passaram por ele.)
final class LabMemoryPeak {
    private let lock = NSLock()
    private var running = false
    private var peak: UInt64 = 0
    private let finished = DispatchSemaphore(value: 0)

    func start() {
        lock.lock()
        running = true
        peak = LabMemory.footprint()
        lock.unlock()
        DispatchQueue.global(qos: .utility).async {
            while true {
                let now = LabMemory.footprint()
                self.lock.lock()
                if now > self.peak { self.peak = now }
                let keepGoing = self.running
                self.lock.unlock()
                if !keepGoing { break }
                usleep(20_000)
            }
            self.finished.signal()
        }
    }

    /// Para de medir e devolve o pico (bytes).
    func stop() -> UInt64 {
        lock.lock()
        running = false
        lock.unlock()
        finished.wait()
        lock.lock()
        let result = peak
        lock.unlock()
        return result
    }
}
