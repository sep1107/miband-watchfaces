# P67 iPhone read-only probe

This folder contains a discovery-only CoreBluetooth probe for Xiaomi Smart Band 10 Pro / M2551B1.

It records:

- the advertised device name and service UUIDs;
- whether service `FE95` is present after connection;
- whether characteristics `005E` and `005F` are present;
- the CoreBluetooth properties exposed by each characteristic.

It deliberately does **not**:

- request or store the Xiaomi AuthKey;
- authenticate a session;
- enable notifications;
- write any characteristic;
- request the watchface list;
- upload, activate, replace or delete a watchface.

The first physical-device test should only run this probe and export its JSON report. A positive result proves that the Xiaomi BLE/GATT transport is visible to iOS; it does not yet prove that authenticated watchface upload works.
