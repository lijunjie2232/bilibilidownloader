from pathlib import Path

import avmerger
from loguru import logger

_QN_240P = 6
_QN_360P = 16
_QN_480P = 32
_QN_720P = 64
_QN_720P_60 = 74
_QN_1080P = 80

_ACODEC_64K = 30216
_ACODEC_132K = 30232
_ACODEC_192K = 30280
_ACODEC_DB = 30250
_ACODEC_HR = 30251

_CODEC_AVC = 7
_CODEC_HEVC = 12
_CODEC_AV1 = 13

_VQ = {
    6: "240P",
    16: "360P",
    32: "480P",
    64: "720P",
    80: "1080P",
}

_AQ = {
    30216: "64K",
    30232: "132K",
    30280: "192K",
    30250: "DB",
    30251: "HR",
}

_CODECID = {
    7: "AVC",
    12: "HEVC",
    13: "AV1",
}


def get_vq(video_quality):
    if video_quality in _VQ:
        return _VQ[video_quality]
    return None


def get_aq(audio_quality):
    if audio_quality in _AQ:
        return _AQ[audio_quality]
    return None


def get_codec(codec_id):
    if codec_id in _CODECID:
        return _CODECID[codec_id]
    return None


def m4s_merger(video_path, audio_path, output_path):
    if isinstance(video_path, Path):
        video_path = video_path.absolute().as_posix()
    if isinstance(audio_path, Path):
        audio_path = audio_path.absolute().as_posix()
    if isinstance(output_path, Path):
        output_path = output_path.absolute().as_posix()

    merger = avmerger.AudioVideoMerger()
    success = merger.merge(video_path, audio_path, output_path)

    if success:
        logger.info("Merge successful!")
    else:
        error = merger.get_last_error()
        logger.error(f"Merge failed: {error}")
