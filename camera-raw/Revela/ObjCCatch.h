#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

/// Roda o bloco e devolve a exceção do Objective-C, se houver.
/// O Swift não consegue pegar NSException sozinho; sem isto, um comando recusado pela câmera fecha o app.
NSException * _Nullable RevelaCatch(NS_NOESCAPE void (^block)(void));

NS_ASSUME_NONNULL_END
