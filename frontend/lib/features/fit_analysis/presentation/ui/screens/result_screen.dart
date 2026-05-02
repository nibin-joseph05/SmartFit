import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/fit_provider.dart';

class ResultScreen extends ConsumerWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(fitProvider);

    return Scaffold(
      appBar: AppBar(title: const Text("Your Try-On Result")),
      body: state.when(
        data: (fitResult) {
          if (fitResult == null) {
            return const Center(child: Text("No result available."));
          }
          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Container(
                  color: Colors.black12,
                  child: Image.network(
                    fitResult.generatedImageUrl,
                    fit: BoxFit.contain,
                    height: MediaQuery.of(context).size.height * 0.6,
                    errorBuilder: (context, error, stackTrace) =>
                        const Center(child: Icon(Icons.broken_image, size: 100, color: Colors.grey)),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Text(
                        fitResult.message,
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 10),
                      Text("Confidence: ${(fitResult.confidence * 100).toStringAsFixed(1)}%"),
                      const SizedBox(height: 30),
                      ElevatedButton(
                        onPressed: () => Navigator.pop(context),
                        style: ElevatedButton.styleFrom(minimumSize: const Size(double.infinity, 50)),
                        child: const Text("Done", style: TextStyle(fontSize: 18)),
                      )
                    ],
                  ),
                )
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text("Error: $e")),
      ),
    );
  }
}
