import CoreBluetooth
import Foundation

/// Discovery-only probe for Xiaomi Smart Band 10 Pro / P67.
///
/// This class intentionally does not authenticate, enable notifications, write
/// characteristics, upload files, activate faces, or delete anything.
@MainActor
final class P67ReadOnlyProbe: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    struct CharacteristicReport: Codable, Equatable {
        let uuid: String
        let properties: [String]
    }

    struct Report: Codable, Equatable {
        var deviceName: String?
        var peripheralIdentifier: String?
        var advertisedServiceUUIDs: [String] = []
        var discoveredServiceUUIDs: [String] = []
        var characteristics: [CharacteristicReport] = []
        var error: String?
        var complete = false
    }

    static let service = CBUUID(string: "0000FE95-0000-1000-8000-00805F9B34FB")
    static let characteristic005E = CBUUID(string: "0000005E-0000-1000-8000-00805F9B34FB")
    static let characteristic005F = CBUUID(string: "0000005F-0000-1000-8000-00805F9B34FB")

    private var central: CBCentralManager!
    private var target: CBPeripheral?
    private(set) var report = Report()
    var onUpdate: ((Report) -> Void)?

    override init() {
        super.init()
        central = CBCentralManager(delegate: self, queue: .main)
    }

    func start() {
        report = Report()
        guard central.state == .poweredOn else {
            report.error = "Bluetooth is not powered on"
            publish()
            return
        }
        // Scan without a service filter: some firmware may omit FE95 from the
        // advertisement even though it is present after connection.
        central.scanForPeripherals(withServices: nil, options: [
            CBCentralManagerScanOptionAllowDuplicatesKey: false,
        ])
    }

    func stop() {
        central.stopScan()
        if let target {
            central.cancelPeripheralConnection(target)
        }
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if central.state != .poweredOn {
            report.error = "Bluetooth state: \(central.state.rawValue)"
            publish()
        }
    }

    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        let localName = advertisementData[CBAdvertisementDataLocalNameKey] as? String
        let name = peripheral.name ?? localName ?? ""
        guard name.hasPrefix("Xiaomi Smart Band 10 Pro") else { return }

        central.stopScan()
        target = peripheral
        peripheral.delegate = self
        report.deviceName = name
        report.peripheralIdentifier = peripheral.identifier.uuidString
        report.advertisedServiceUUIDs = (
            advertisementData[CBAdvertisementDataServiceUUIDsKey] as? [CBUUID] ?? []
        ).map(\.uuidString).sorted()
        publish()
        central.connect(peripheral, options: nil)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        peripheral.discoverServices([Self.service])
    }

    func centralManager(
        _ central: CBCentralManager,
        didFailToConnect peripheral: CBPeripheral,
        error: Error?
    ) {
        report.error = error?.localizedDescription ?? "Connection failed"
        report.complete = true
        publish()
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        if let error {
            report.error = error.localizedDescription
            report.complete = true
            publish()
            return
        }
        let services = peripheral.services ?? []
        report.discoveredServiceUUIDs = services.map { $0.uuid.uuidString }.sorted()
        guard let service = services.first(where: { $0.uuid == Self.service }) else {
            report.error = "FE95 service was not found"
            report.complete = true
            publish()
            central.cancelPeripheralConnection(peripheral)
            return
        }
        peripheral.discoverCharacteristics(
            [Self.characteristic005E, Self.characteristic005F],
            for: service
        )
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverCharacteristicsFor service: CBService,
        error: Error?
    ) {
        if let error {
            report.error = error.localizedDescription
        } else {
            report.characteristics = (service.characteristics ?? []).map {
                CharacteristicReport(
                    uuid: $0.uuid.uuidString,
                    properties: Self.propertyNames($0.properties)
                )
            }.sorted { $0.uuid < $1.uuid }
        }
        report.complete = true
        publish()
        central.cancelPeripheralConnection(peripheral)
    }

    func json() throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return try encoder.encode(report)
    }

    private func publish() {
        onUpdate?(report)
    }

    private static func propertyNames(_ properties: CBCharacteristicProperties) -> [String] {
        var names: [String] = []
        if properties.contains(.read) { names.append("read") }
        if properties.contains(.write) { names.append("write") }
        if properties.contains(.writeWithoutResponse) { names.append("writeWithoutResponse") }
        if properties.contains(.notify) { names.append("notify") }
        if properties.contains(.indicate) { names.append("indicate") }
        return names
    }
}
