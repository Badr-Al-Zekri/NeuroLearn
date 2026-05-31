import 'package:flutter_riverpod/flutter_riverpod.dart';

final telemetryProvider = StateNotifierProvider<TelemetryController, List<TelemetryEvent>>((ref) {
  return TelemetryController();
});

class TelemetryEvent {
  const TelemetryEvent({required this.name, required this.createdAt, required this.properties});
  final String name;
  final DateTime createdAt;
  final Map<String, Object?> properties;
}

class TelemetryController extends StateNotifier<List<TelemetryEvent>> {
  TelemetryController() : super(const []);

  bool get isReturnSession => state.any((event) => event.name == 'session_completed');

  void track(String name, Map<String, Object?> properties) {
    final event = TelemetryEvent(
      name: name,
      createdAt: DateTime.now(),
      properties: {
        ...properties,
        'return_session': isReturnSession,
      },
    );
    state = [...state, event];
  }

  void trackDropOff(String point, {String? documentId}) {
    track('drop_off', {
      'point': point,
      if (documentId != null) 'document_id': documentId,
    });
  }

  int count(String name) => state.where((event) => event.name == name).length;
}
