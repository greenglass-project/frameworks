/******************************************************************************
*  Copyright 2024 Greenglass Project
 *
 *  Use of this source code is governed by an MIT-style
 *  license that can be found in the LICENSE file or at
 *  https://opensource.org/licenses/MIT.
 *
 *****************************************************************************/
#include <string.h>
#include <stdio.h>

#include "py/runtime.h"
#include "py/obj.h"
#include "py/objlist.h"

#include "py/objstr.h"
#include "py/objarray.h"

#include "tahu.pb.h"
#include "pb_encode.h"
#include "pb_decode.h"

#include "pb.h"

#include "mpspk.h"

// -----------------------------------------------------
// Metric
// -----------------------------------------------------
static mp_obj_t mpspk_Metric_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    if (n_args != 4)
        mp_raise_ValueError("4 arguments expected 'name' 'type' 'value' 'timestamp'");

    mpspk_Metric_obj_t *self = (mpspk_Metric_obj_t *)mp_obj_malloc(mpspk_Metric_obj_t, type);
    memset(&self->metric, 0, sizeof(mpspk_Payload_Metric));

	self->metric.name = (char*)mp_obj_str_get_str(args[0]);
	self->metric.has_datatype = true;;
   	self-> metric.datatype = mp_obj_get_int(args[1]);

	//mp_printf(MP_PYTHON_PRINTER, "name %s\n",self->metric.name);
	//mp_printf(MP_PYTHON_PRINTER, "datatype %d\n",self->metric.datatype);

    switch (self->metric.datatype) {
    	case METRIC_DATA_TYPE_INT8 : // 1
      	case METRIC_DATA_TYPE_INT16: // 2
      	case METRIC_DATA_TYPE_INT32: // 3
      	case METRIC_DATA_TYPE_UINT8: // 5
      	case METRIC_DATA_TYPE_UINT16: // 6
      	case METRIC_DATA_TYPE_UINT32: // 7
        	self->metric.value.int_value = mp_obj_get_int(args[2]);
          	break;

      	case METRIC_DATA_TYPE_INT64: // 4
      	case METRIC_DATA_TYPE_UINT64: // 9
    		self->metric.value.long_value = (long)mp_obj_get_int(args[2]);
    		break;
  
      case METRIC_DATA_TYPE_FLOAT: // 9
      		self->metric.value.float_value = mp_obj_get_float(args[2]);
    		break;
                
      case METRIC_DATA_TYPE_DOUBLE: // 10
      		self->metric.value.double_value = (double)mp_obj_get_float(args[2]);
    		break;

      //case METRIC_DATA_TYPE_BOOLEAN:
      //  self->value.bool_value = mp_obj_get_bool(args[2]);
      //  break;

      case METRIC_DATA_TYPE_STRING: // 12
           self->metric.value.string_value = (char*)mp_obj_str_get_str(args[2]);
           break;

      default:
           mp_raise_ValueError("Unknown metric data type");

    }
    self->metric.timestamp = mp_obj_get_int(args[3]);

    return MP_OBJ_FROM_PTR(self);
}

static void mpspk_Metric_attribute_handler(mp_obj_t self_in, qstr attr, mp_obj_t *dest) {
    mpspk_Metric_obj_t *self = MP_OBJ_TO_PTR(self_in);
 	switch(attr) {
    	case MP_QSTR_name:
    		//mp_printf(MP_PYTHON_PRINTER, "name %s\n",self->metric.name);

        	if (dest[0] == MP_OBJ_NULL)  // Read
        		dest[0] = mp_obj_new_str_from_cstr(self->metric.name);
            break;
        case MP_QSTR_type:
       		if (dest[0] == MP_OBJ_NULL)  // Read
        		dest[0] = mp_obj_new_int(self->metric.datatype);
            break;
        case MP_QSTR_value:
       		if (dest[0] == MP_OBJ_NULL) {
                  switch(self->metric.datatype) {
                    case METRIC_DATA_TYPE_INT8 : // 1
      				case METRIC_DATA_TYPE_INT16: // 2
     				case METRIC_DATA_TYPE_INT32: // 3
      				case METRIC_DATA_TYPE_UINT8: // 5
      				case METRIC_DATA_TYPE_UINT16: // 6
      				case METRIC_DATA_TYPE_UINT32: // 7
        				dest[0] = mp_obj_new_int(self->metric.value.int_value);
          				break;

                  	case METRIC_DATA_TYPE_INT64: // 4
                  	case METRIC_DATA_TYPE_UINT64: // 9
                  		dest[0] = mp_obj_new_int(self->metric.value.long_value);
						break;

      				case METRIC_DATA_TYPE_FLOAT: // 9
      					dest[0] = mp_obj_new_float(self->metric.value.float_value);
                  		break;

      				case METRIC_DATA_TYPE_DOUBLE: // 10
                        dest[0] = mp_obj_new_float(self->metric.value.double_value);
         				break;

      				//case METRIC_DATA_TYPE_BOOLEAN:
      				//  self->value.bool_value = mp_obj_get_bool(args[2]);
      				//  break;

      				case METRIC_DATA_TYPE_STRING: // 12
                    	dest[0] = mp_obj_new_str_from_cstr(self->metric.value.string_value);
           				break;
                  }
             }
             break;

        case MP_QSTR_timestamp:
       		if (dest[0] == MP_OBJ_NULL) {// Read
            	dest[0] = mp_obj_new_int(self->metric.timestamp);
            }
            break;

        default:
        	dest[1] = MP_OBJ_SENTINEL;
    }
   	return;
}

static const mp_rom_map_elem_t mpspk_Metric_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_INT8), MP_ROM_INT( METRIC_DATA_TYPE_INT8) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_INT16), MP_ROM_INT( METRIC_DATA_TYPE_INT16) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_INT32), MP_ROM_INT( METRIC_DATA_TYPE_INT32) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_INT64), MP_ROM_INT( METRIC_DATA_TYPE_INT64) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_UINT8), MP_ROM_INT( METRIC_DATA_TYPE_UINT8) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_UINT16), MP_ROM_INT( METRIC_DATA_TYPE_UINT16) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_UINT32), MP_ROM_INT( METRIC_DATA_TYPE_UINT32) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_UINT64), MP_ROM_INT( METRIC_DATA_TYPE_UINT64) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_FLOAT), MP_ROM_INT( METRIC_DATA_TYPE_FLOAT) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_DOUBLE), MP_ROM_INT( METRIC_DATA_TYPE_DOUBLE) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_BOOLEAN), MP_ROM_INT( METRIC_DATA_TYPE_BOOLEAN) },
 	{ MP_ROM_QSTR(MP_QSTR_METRIC_DATA_TYPE_STRING), MP_ROM_INT( METRIC_DATA_TYPE_STRING) }
};
static MP_DEFINE_CONST_DICT(mpspk_Metric_locals_dict, mpspk_Metric_locals_dict_table);

// This defines the type(Timer) object.
MP_DEFINE_CONST_OBJ_TYPE(
    mpspk_type_Metric,
    MP_QSTR_Metric,
    MP_TYPE_FLAG_NONE,
    make_new, &mpspk_Metric_make_new,
    attr, &mpspk_Metric_attribute_handler,
    locals_dict, &mpspk_Metric_locals_dict
    );

// -----------------------------------------------------
// PayloadIn
// -----------------------------------------------------

static mp_obj_t mpspk_PayloadIn_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {

 	if (n_args != 1)
        mp_raise_ValueError("1 arguments expected 'smessager'");

    // Get the passed bytearray and convert it to a stream
	mp_obj_array_t *buffer = MP_OBJ_TO_PTR(args[0]);
    mp_printf(MP_PYTHON_PRINTER, "buffer length %d %d\n", buffer->len, sizeof(buffer->items));
    pb_istream_t node_stream = pb_istream_from_buffer(buffer->items, buffer->len);

    // Create the PayloadIn object and zero the internal payload
    mpspk_PayloadIn_obj_t *self = (mpspk_PayloadIn_obj_t*)mp_obj_malloc_with_finaliser(mpspk_PayloadIn_obj_t, type);
    memset(&self->payload, 0, sizeof(mpspk_Payload));

    // Decode the stream into the internal payload
    const bool decode_result = pb_decode(&node_stream, org_eclipse_tahu_protobuf_Payload_fields, &self->payload);

    if(!decode_result) {
      mp_raise_ValueError(PB_GET_ERROR(&node_stream));
    	//mp_raise_ValueError("Failed to decode payload");
    }
    //mp_printf(MP_PYTHON_PRINTER, "number of metrics %d\n", self->payload.metrics_count);

    return MP_OBJ_FROM_PTR(self);
}

static void mpspk_PatloadIn_attribute_handler(mp_obj_t self_in, qstr attr, mp_obj_t *dest) {

      mpspk_PayloadIn_obj_t *self = MP_OBJ_TO_PTR(self_in);

      switch(attr) {

        case MP_QSTR_seq: {
          	if (dest[0] == MP_OBJ_NULL) {
        		dest[0] = mp_obj_new_int_from_uint(self->payload.seq);
            }
			break;
        }
        case MP_QSTR_timestamp: {
          	if (dest[0] == MP_OBJ_NULL) {
        		dest[0] = mp_obj_new_int_from_uint(self->payload.timestamp);
            }
			break;
        }
        case MP_QSTR_uuid: {
          	if (dest[0] == MP_OBJ_NULL) {
        		dest[0] = mp_obj_new_str_from_cstr(self->payload.uuid);
            }
			break;
        }
        case MP_QSTR_metrics_count: {
        	if (dest[0] == MP_OBJ_NULL) {
				dest[0] = mp_obj_new_int_from_uint(self->payload.metrics_count);
          	}
            break;
        }

        default:
        	dest[1] = MP_OBJ_SENTINEL;
      }
}

static mp_obj_t mpspk_PayloadIn_metric(mp_obj_t self_in, mp_obj_t index_in) {
    mpspk_PayloadIn_obj_t *self = MP_OBJ_TO_PTR(self_in);
    int index = mp_obj_get_int(index_in);
	if(index < 0 || index >= self->payload.metrics_count) {
    	mp_raise_ValueError("Invalid index");
    }

    mpspk_Metric_obj_t *metric_obj = (mpspk_Metric_obj_t *)mp_obj_malloc(mpspk_Metric_obj_t, &mpspk_type_Metric);
    metric_obj->metric = self->payload.metrics[index];

    return MP_OBJ_FROM_PTR(metric_obj);
}
static MP_DEFINE_CONST_FUN_OBJ_2(mpspk_PayloadIn_metric_obj, mpspk_PayloadIn_metric);

// Free the payload's internal data
static void *mpspk_PayloadIn_free(mp_obj_t self_in) {
    mpspk_PayloadIn_obj_t *self = MP_OBJ_TO_PTR(self_in);
    pb_release(org_eclipse_tahu_protobuf_Payload_fields, &self->payload);
    return NULL;
}
static MP_DEFINE_CONST_FUN_OBJ_1(mpspk_PayloadIn_free_obj, mpspk_PayloadIn_free);

static const mp_rom_map_elem_t mpspk_PayloadIn_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR__del__), MP_ROM_PTR(&mpspk_PayloadIn_free_obj) },
    { MP_ROM_QSTR(MP_QSTR_metric), MP_ROM_PTR(&mpspk_PayloadIn_metric_obj) }

};
static MP_DEFINE_CONST_DICT(mpspk_PayloadIn_locals_dict, mpspk_PayloadIn_locals_dict_table);

// This defines the type(Timer) object.
MP_DEFINE_CONST_OBJ_TYPE(
    mpspk_type_PayloadIn,
    MP_QSTR_PayloadIn,
    MP_TYPE_FLAG_NONE,
    make_new, &mpspk_PayloadIn_make_new,
    attr, mpspk_PatloadIn_attribute_handler,
    locals_dict, &mpspk_PayloadIn_locals_dict
    );

// -----------------------------------------------------
// PayloadOut
// -----------------------------------------------------

static mp_obj_t mpspk_PayloadOut_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {

     if (n_args != 3)
        mp_raise_ValueError("3 arguments expected 'seq_nr' 'uuid' 'timestamp'");
    mpspk_PayloadOut_obj_t *self = (mpspk_PayloadOut_obj_t*)mp_obj_malloc_with_finaliser(mpspk_PayloadOut_obj_t, type);
    memset(&self->payload, 0, sizeof(mpspk_Payload));

	self->payload.has_timestamp = true;
	self->payload.timestamp = mp_obj_get_int(args[2]);
    self->payload.has_seq = true;
    self->payload.seq = mp_obj_get_int(args[0]);
    self->payload.uuid = (char*)mp_obj_str_get_str(args[1]);
    return MP_OBJ_FROM_PTR(self);
}

static void *mpspk_PayloadOut_add_metric(void *self_in, void* metric_in) {
	mpspk_PayloadOut_obj_t *self = MP_OBJ_TO_PTR(self_in);
	mpspk_Metric_obj_t *metric = MP_OBJ_TO_PTR(metric_in);

	const int old_count = self->payload.metrics_count;
	const int new_count = (old_count + 1);

	const size_t new_allocation_size = sizeof(mpspk_Payload_Metric) * new_count;
	void *realloc_result = m_realloc(self->payload.metrics, new_allocation_size);
	if (realloc_result == NULL) {
		mp_raise_ValueError("realloc failed");
	}
	self->payload.metrics = realloc_result;
	self->payload.metrics_count = new_count;
	memcpy(&self->payload.metrics[old_count], &metric->metric, sizeof(mpspk_Payload_Metric));
        
	return MP_OBJ_FROM_PTR(self);
}

static MP_DEFINE_CONST_FUN_OBJ_2(mpspk_PayloadOut_add_metric_obj, &mpspk_PayloadOut_add_metric);

static mp_obj_t mpspk_PayloadOut_to_bytes(const mp_obj_t self_in) {

  	mpspk_PayloadOut_obj_t *self = MP_OBJ_TO_PTR(self_in);

   	pb_ostream_t sizing_stream = PB_OSTREAM_SIZING;
    bool encode_result = pb_encode(&sizing_stream, org_eclipse_tahu_protobuf_Payload_fields, &self->payload);
    if (!encode_result)
    	mp_raise_ValueError("Encoding failed");

    const size_t message_length = sizing_stream.bytes_written;

   	pb_byte_t *message_buffer = (pb_byte_t *)m_malloc(message_length * sizeof(pb_byte_t));
    pb_ostream_t buffer_stream = pb_ostream_from_buffer(message_buffer, message_length);

	encode_result = pb_encode(&buffer_stream, org_eclipse_tahu_protobuf_Payload_fields, &self->payload);
    if (!encode_result) {
    	mp_raise_ValueError("Encoding failed");
	}

    mp_obj_t msg =  mp_obj_new_bytearray(message_length, message_buffer);
	return MP_OBJ_FROM_PTR(msg);
}

static MP_DEFINE_CONST_FUN_OBJ_1(mpspk_PayloadOut_to_bytes_obj, mpspk_PayloadOut_to_bytes);

// Free the payload's internal data
static void *mpspk_PayloadOut_free(mp_obj_t self_in) {
    mpspk_PayloadOut_obj_t *self = MP_OBJ_TO_PTR(self_in);
    pb_release(org_eclipse_tahu_protobuf_Payload_fields, &self->payload);
    return NULL;
}
static MP_DEFINE_CONST_FUN_OBJ_1(mpspk_PayloadOut_free_obj, mpspk_PayloadOut_free);


static const mp_rom_map_elem_t mpspk_PayloadOut_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR__del__), MP_ROM_PTR(&mpspk_PayloadOut_free_obj) },
	{ MP_ROM_QSTR(MP_QSTR_add_metric), MP_ROM_PTR(&mpspk_PayloadOut_add_metric_obj) },
	{ MP_ROM_QSTR(MP_QSTR_to_bytes), MP_ROM_PTR(&mpspk_PayloadOut_to_bytes_obj) }
};

static MP_DEFINE_CONST_DICT(mpspk_PayloadOut_locals_dict, mpspk_PayloadOut_locals_dict_table);

// This defines the type(Timer) object.
MP_DEFINE_CONST_OBJ_TYPE(
    mpspk_type_PayloadOut,
    MP_QSTR_PayloadOut,
    MP_TYPE_FLAG_NONE,
    make_new, &mpspk_PayloadOut_make_new,
    locals_dict, &mpspk_PayloadOut_locals_dict
    );

// -----------------------------------------------------
// mpspk
// -----------------------------------------------------

static const mp_rom_map_elem_t mpspk_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_mpspk) },
    { MP_ROM_QSTR(MP_QSTR_Metric), MP_ROM_PTR(&mpspk_type_Metric) },
    { MP_ROM_QSTR(MP_QSTR_PayloadOut), MP_ROM_PTR(&mpspk_type_PayloadOut) },
    { MP_ROM_QSTR(MP_QSTR_PayloadIn), MP_ROM_PTR(&mpspk_type_PayloadIn) },
};
static MP_DEFINE_CONST_DICT(mpspk_module_globals, mpspk_module_globals_table);

// Define module object.
const mp_obj_module_t mpspk_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&mpspk_module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_mpspk, mpspk_user_cmodule);