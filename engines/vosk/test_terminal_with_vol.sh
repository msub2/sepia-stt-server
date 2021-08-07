#!/bin/bash
if [ -n "$(uname -m | grep aarch64)" ]; then
	IMAGE_TAG=vosk_aarch64
elif [ -n "$(uname -m | grep armv7l)" ]; then
	IMAGE_TAG=vosk_armv7l
else
	IMAGE_TAG=vosk_amd64
fi
HOST_MODELS="$(realpath ~)/stt/models"
HOST_SHARE="$(realpath ~)/stt/share"
mkdir -p "$HOST_MODELS"
mkdir -p "$HOST_SHARE"
sudo docker run --rm --name=sepia-stt -p 20741:20741 -it \
	-v "$HOST_MODELS":/home/admin/sepia-stt/models/my \
	-v "$HOST_SHARE":/home/admin/sepia-stt/share \
	--env SEPIA_STT_SETTINGS=/home/admin/sepia-stt/share/my.conf \
	sepia/stt-server:$IMAGE_TAG \
	/bin/bash
