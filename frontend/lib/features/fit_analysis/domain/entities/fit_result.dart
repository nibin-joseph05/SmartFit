class FitResult {
  final String recommendedSize;
  final String fitClassification;
  final double confidence;

  FitResult({
    required this.recommendedSize,
    required this.fitClassification,
    required this.confidence,
  });
}
