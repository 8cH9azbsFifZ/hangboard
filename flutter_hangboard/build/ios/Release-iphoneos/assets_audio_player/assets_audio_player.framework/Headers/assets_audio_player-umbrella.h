#ifdef __OBJC__
#import <UIKit/UIKit.h>
#else
#ifndef FOUNDATION_EXPORT
#if defined(__cplusplus)
#define FOUNDATION_EXPORT extern "C"
#else
#define FOUNDATION_EXPORT extern
#endif
#endif
#endif

#import "AssetsAudioPlayerPlugin.h"

FOUNDATION_EXPORT double assets_audio_playerVersionNumber;
FOUNDATION_EXPORT const unsigned char assets_audio_playerVersionString[];

