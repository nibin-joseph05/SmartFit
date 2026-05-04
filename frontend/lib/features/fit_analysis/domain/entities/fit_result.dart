class FitResult {
  final String generatedImageUrl;
  final String message;
  final double confidence;

  FitResult({
    required this.generatedImageUrl,
    required this.message,
    required this.confidence,
  });
}