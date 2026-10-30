#import "ObjCCatch.h"

NSException * _Nullable RevelaCatch(NS_NOESCAPE void (^block)(void)) {
    @try {
        block();
        return nil;
    } @catch (NSException *exception) {
        return exception;
    }
}
