#!/bin/bash

UI_PROJ_ROOT=$(git rev-parse --show-toplevel)/UMTK_UI/v1.5/

# Make windows packages
WIN_BUILD_DIR=${UI_PROJ_ROOT}/build/windows
mkdir -p ${WIN_BUILD_DIR}

cp -r ${UI_PROJ_ROOT}/img ${WIN_BUILD_DIR}
mkdir ${WIN_BUILD_DIR}/lib
cp  ${UI_PROJ_ROOT}/lib/*.py ${WIN_BUILD_DIR}/lib
cp -r ${UI_PROJ_ROOT}/style ${WIN_BUILD_DIR}
cp ${UI_PROJ_ROOT}/*.py ${WIN_BUILD_DIR}
cp ${UI_PROJ_ROOT}/requirements.txt ${WIN_BUILD_DIR}
cp ${UI_PROJ_ROOT}/package/script/windows/* ${WIN_BUILD_DIR}


# Make mac packages
MAC_BUILD_DIR=${UI_PROJ_ROOT}/build/mac
mkdir -p ${MAC_BUILD_DIR}

cp -r ${UI_PROJ_ROOT}/img ${MAC_BUILD_DIR}
mkdir ${MAC_BUILD_DIR}/lib
cp  ${UI_PROJ_ROOT}/lib/*.py ${MAC_BUILD_DIR}/lib
cp -r ${UI_PROJ_ROOT}/style ${MAC_BUILD_DIR}
cp ${UI_PROJ_ROOT}/*.py ${MAC_BUILD_DIR}
cp ${UI_PROJ_ROOT}/requirements.txt ${MAC_BUILD_DIR}
cp ${UI_PROJ_ROOT}/package/script/mac/* ${MAC_BUILD_DIR}

