/******************************************************************************
*  Copyright 2024 Greenglass Project
 *
 *  Use of this source code is governed by an MIT-style
 *  license that can be found in the LICENSE file or at
 *  https://opensource.org/licenses/MIT.
 *
 *****************************************************************************/
#ifndef SPARKPLUG_H
#define SPARKPLUG_H

#include "py/runtime.h"
#include "tahu.pb.h"

typedef org_eclipse_tahu_protobuf_Payload mpspk_Payload;
typedef org_eclipse_tahu_protobuf_Payload_Metric mpspk_Payload_Metric;

#define METRIC_DATA_TYPE_UNKNOWN 0
#define METRIC_DATA_TYPE_INT8 1
#define METRIC_DATA_TYPE_INT16 2
#define METRIC_DATA_TYPE_INT32 3
#define METRIC_DATA_TYPE_INT64 4
#define METRIC_DATA_TYPE_UINT8 5
#define METRIC_DATA_TYPE_UINT16 6
#define METRIC_DATA_TYPE_UINT32 7
#define METRIC_DATA_TYPE_UINT64 8
#define METRIC_DATA_TYPE_FLOAT 9
#define METRIC_DATA_TYPE_DOUBLE 10
#define METRIC_DATA_TYPE_BOOLEAN 11
#define METRIC_DATA_TYPE_STRING 12
//#define METRIC_DATA_TYPE_DATETIME 13
//#define METRIC_DATA_TYPE_TEXT 14
//#define METRIC_DATA_TYPE_UUID 15
//#define METRIC_DATA_TYPE_DATASET 16
//#define METRIC_DATA_TYPE_BYTES 17
//#define METRIC_DATA_TYPE_FILE 18
//#define METRIC_DATA_TYPE_TEMPLATE 19

typedef struct _mpspk_Metric_obj {
    mp_obj_base_t base;
    mpspk_Payload_Metric metric;
} mpspk_Metric_obj_t;

typedef struct _mpspk_PayloadIn_obj {
    mp_obj_base_t base;
    mpspk_Payload payload;
} mpspk_PayloadIn_obj_t;

typedef struct _mpspk_PayloadOut_obj {
    mp_obj_base_t base;
    mpspk_Payload payload;
} mpspk_PayloadOut_obj_t;

typedef struct _mpspk_Test_obj {
    mp_obj_base_t base;
    int value;
} mpspk_Test_obj_t;

#endif //SPARKPLUG_H
