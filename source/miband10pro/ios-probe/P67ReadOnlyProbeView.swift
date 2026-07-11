import SwiftUI

@MainActor
final class P67ProbeViewModel: ObservableObject {
    @Published private(set) var reportText = "Tap Start discovery to inspect the P67 BLE services."
    @Published private(set) var isRunning = false
    @Published private(set) var isComplete = false

    private var probe: P67ReadOnlyProbe?

    func start() {
        let nextProbe = P67ReadOnlyProbe()
        probe = nextProbe
        isRunning = true
        isComplete = false
        reportText = "Scanning for Xiaomi Smart Band 10 Pro..."

        nextProbe.onUpdate = { [weak self] report in
            guard let self else { return }
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            if let data = try? encoder.encode(report),
               let text = String(data: data, encoding: .utf8) {
                self.reportText = text
            }
            self.isComplete = report.complete
            if report.complete {
                self.isRunning = false
            }
        }
        nextProbe.start()
    }

    func stop() {
        probe?.stop()
        isRunning = false
    }
}

struct P67ReadOnlyProbeView: View {
    @StateObject private var model = P67ProbeViewModel()

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                Text("Discovery only: this screen cannot authenticate, write, upload, activate or delete a watchface.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)

                ScrollView {
                    Text(model.reportText)
                        .font(.system(.footnote, design: .monospaced))
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                }
                .background(.quaternary, in: RoundedRectangle(cornerRadius: 12))

                HStack {
                    Button(model.isRunning ? "Scanning..." : "Start discovery") {
                        model.start()
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(model.isRunning)

                    Button("Stop") {
                        model.stop()
                    }
                    .buttonStyle(.bordered)
                    .disabled(!model.isRunning)

                    ShareLink(item: model.reportText) {
                        Label("Share JSON", systemImage: "square.and.arrow.up")
                    }
                    .disabled(!model.isComplete)
                }
            }
            .padding()
            .navigationTitle("P67 BLE Probe")
        }
    }
}
