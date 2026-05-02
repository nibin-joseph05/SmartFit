import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:smartfit/features/fit_analysis/presentation/providers/fit_provider.dart';

class ResultScreen extends ConsumerWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(fitProvider);

    return Scaffold(
      appBar: AppBar(title: const Text("Your Fit Result")),
      body: Center(
        child: state.when(
          data: (fitResult) {
            if (fitResult == null) {
              return const Text("No result available.");
            }
            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  "Size: ${fitResult.recommendedSize}",
                  style: const TextStyle(fontSize: 40, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 10),
                Text("Fit: ${fitResult.fitClassification}", style: const TextStyle(fontSize: 20)),
                const SizedBox(height: 10),
                Text("Confidence: ${(fitResult.confidence * 100).toStringAsFixed(1)}%"),
              ],
            );
          },
          loading: () => const CircularProgressIndicator(),
          error: (e, _) => Text("Error: $e"),
        ),
      ),
    );
  }
}
