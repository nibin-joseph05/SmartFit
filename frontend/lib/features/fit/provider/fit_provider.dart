import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/fit_api.dart';

final fitProvider = StateNotifierProvider<FitNotifier, AsyncValue<Map<String, dynamic>>>(
  (ref) => FitNotifier(),
);

class FitNotifier extends StateNotifier<AsyncValue<Map<String, dynamic>>> {
  FitNotifier() : super(const AsyncValue.data({}));

  final FitApi _api = FitApi();

  Future<void> getFit(Map<String, dynamic> data) async {
    state = const AsyncValue.loading();
    try {
      final result = await _api.getSize(data);
      state = AsyncValue.data(result);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}