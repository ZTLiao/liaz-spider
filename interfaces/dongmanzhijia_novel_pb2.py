# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: dongmanzhijia_novel.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19\x64ongmanzhijia_novel.proto\x12\x13\x64ongmanzhijia_novel\"W\n\x17NovelChapterDetailProto\x12\x11\n\tchapterId\x18\x01 \x01(\x03\x12\x13\n\x0b\x63hapterName\x18\x02 \x01(\t\x12\x14\n\x0c\x63hapterOrder\x18\x03 \x01(\x05\"\x85\x01\n\x10NovelVolumeProto\x12\x10\n\x08volumeId\x18\x01 \x01(\x03\x12\x10\n\x08lnovelId\x18\x02 \x01(\x03\x12\x12\n\nvolumeName\x18\x03 \x01(\t\x12\x13\n\x0bvolumeOrder\x18\x04 \x01(\x05\x12\x0f\n\x07\x61\x64\x64time\x18\x05 \x01(\x03\x12\x13\n\x0bsumChapters\x18\x06 \x01(\x05\"\x93\x01\n\x16NovelVolumeDetailProto\x12\x10\n\x08volumeId\x18\x01 \x01(\x03\x12\x12\n\nvolumeName\x18\x02 \x01(\t\x12\x13\n\x0bvolumeOrder\x18\x03 \x01(\x05\x12>\n\x08\x63hapters\x18\x04 \x03(\x0b\x32,.dongmanzhijia_novel.NovelChapterDetailProto\"\xae\x03\n\x10NovelDetailProto\x12\x0f\n\x07novelId\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04zone\x18\x03 \x01(\t\x12\x0e\n\x06status\x18\x04 \x01(\t\x12\x1c\n\x14lastUpdateVolumeName\x18\x05 \x01(\t\x12\x1d\n\x15lastUpdateChapterName\x18\x06 \x01(\t\x12\x1a\n\x12lastUpdateVolumeId\x18\x07 \x01(\x03\x12\x1b\n\x13lastUpdateChapterId\x18\x08 \x01(\x03\x12\x16\n\x0elastUpdateTime\x18\t \x01(\x03\x12\r\n\x05\x63over\x18\n \x01(\t\x12\x0f\n\x07hotHits\x18\x0b \x01(\x03\x12\x14\n\x0cintroduction\x18\x0c \x01(\t\x12\r\n\x05types\x18\r \x03(\t\x12\x0f\n\x07\x61uthors\x18\x0e \x01(\t\x12\x13\n\x0b\x66irstLetter\x18\x0f \x01(\t\x12\x14\n\x0csubscribeNum\x18\x10 \x01(\x03\x12\x17\n\x0fredisUpdateTime\x18\x11 \x01(\x03\x12\x35\n\x06volume\x18\x12 \x03(\x0b\x32%.dongmanzhijia_novel.NovelVolumeProto\"u\n\x19NovelChapterResponseProto\x12\r\n\x05\x65rrno\x18\x01 \x01(\x05\x12\x0e\n\x06\x65rrmsg\x18\x02 \x01(\t\x12\x39\n\x04\x64\x61ta\x18\x03 \x03(\x0b\x32+.dongmanzhijia_novel.NovelVolumeDetailProto\"n\n\x18NovelDetailResponseProto\x12\r\n\x05\x65rrno\x18\x01 \x01(\x05\x12\x0e\n\x06\x65rrmsg\x18\x02 \x01(\t\x12\x33\n\x04\x64\x61ta\x18\x03 \x01(\x0b\x32%.dongmanzhijia_novel.NovelDetailProtob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'dongmanzhijia_novel_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_NOVELCHAPTERDETAILPROTO']._serialized_start=50
  _globals['_NOVELCHAPTERDETAILPROTO']._serialized_end=137
  _globals['_NOVELVOLUMEPROTO']._serialized_start=140
  _globals['_NOVELVOLUMEPROTO']._serialized_end=273
  _globals['_NOVELVOLUMEDETAILPROTO']._serialized_start=276
  _globals['_NOVELVOLUMEDETAILPROTO']._serialized_end=423
  _globals['_NOVELDETAILPROTO']._serialized_start=426
  _globals['_NOVELDETAILPROTO']._serialized_end=856
  _globals['_NOVELCHAPTERRESPONSEPROTO']._serialized_start=858
  _globals['_NOVELCHAPTERRESPONSEPROTO']._serialized_end=975
  _globals['_NOVELDETAILRESPONSEPROTO']._serialized_start=977
  _globals['_NOVELDETAILRESPONSEPROTO']._serialized_end=1087
# @@protoc_insertion_point(module_scope)
