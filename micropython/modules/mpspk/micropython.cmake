# Create an INTERFACE library for our C module.
add_library(sparkplug INTERFACE)

# Add our source files to the lib
target_sources(sparkplug INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/pb_common.c
        ${CMAKE_CURRENT_LIST_DIR}/pb_decode.c
        ${CMAKE_CURRENT_LIST_DIR}/pb_encode.c
        ${CMAKE_CURRENT_LIST_DIR}/tahu.pb.c
        ${CMAKE_CURRENT_LIST_DIR}/mpspk.c
)

# Add the current directory as an include directory.
target_include_directories(sparkplug INTERFACE ${CMAKE_CURRENT_LIST_DIR})

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE sparkplug)
