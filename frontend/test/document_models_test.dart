import 'package:flutter_test/flutter_test.dart';
import 'package:neurolearn_ai/shared/models/document_models.dart';

void main() {
  test('DocumentMetadata parses API response', () {
    final document = DocumentMetadata.fromJson({
      'document_id': 'doc-1',
      'title': 'Demo',
      'kind': 'text',
      'word_count': 120,
      'created_at': '2026-05-13T12:00:00Z',
      'features': {'summary': true, 'quiz': true, 'chat': true},
    });

    expect(document.documentId, 'doc-1');
    expect(document.features['chat'], isTrue);
    expect(document.wordCount, 120);
  });
}
