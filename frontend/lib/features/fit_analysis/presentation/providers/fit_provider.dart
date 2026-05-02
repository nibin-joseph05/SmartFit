import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/fit_remote_datasource.dart';
import '../../data/repositories/fit_repository.dart';
import '../../domain/entities/fit_result.dart';

final dioClientProvider = Provider((ref) => DioClient());

final fitRemoteDataSourceProvider = Provider((ref) {
  return FitRemoteDataSource(ref.read(dioClientProvider));
});

final fitRepositoryProvider = Provider((ref) {
  return FitRepository(ref.read(fitRemoteDataSourceProvider));
});

final fitProvider = StateNotifierProvider<FitNotifier, AsyncValue<FitResult?>>((ref) {
  return FitNotifier(ref.read(fitRepositoryProvider));
});

class FitNotifier extends StateNotifier<AsyncValue<FitResult?>> {
  final FitRepository _repository;

  FitNotifier(this._repository) : super(const AsyncValue.data(null));

  Future<void> analyzeFit({
    required double height,
    required double weight,
    required String dressType,
    required File imageFile,
  }) async {
    state = const AsyncValue.loading();
    try {
      final result = await _repository.analyzeFit(
        height: height,
        weight: weight,
        dressType: dressType,
        imageFile: imageFile,
      );
      state = AsyncValue.data(result);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}
