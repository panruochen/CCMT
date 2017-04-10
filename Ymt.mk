######################################################################################################
#
# YUNZ MAKEFILE TEMPLATE
#
# The purpose of implementing this script is help quickly deploy source code
# tree during initial phase of development. It is designed to manage one whole
# project from within one single makefile and to be easily adapted to
# different directory hierarchy by simply setting user configurable variables.
# This script is expected to be used with gcc toolchains on bash-compatible
# shell.
#
# Author:  Pan Ruochen <ijkxyz@msn.com>
# History: 2012/10/10 -- The first version
#          2016/9/4   -- Update
#          2017/4/10  -- Multiple modules in one config file.
#
# You can get the latest version from here:
# https://github.com/panruochen/yunz
#
######################################################################################################
# User Defined Variables
#
# ====================================================================================================
# LOCAL_GCC_PREFIX: The perfix of gnu toolchain.
# ====================================================================================================
# LOCAL_CFLAGS:     Compiler flags.
# LOCAL_C_INCLUDES: Header files include paths.
# LOCAL_SRC_FILES:  Sources. The entriess ending with a trailing / are taken as directories, the others
#                   are taken as files. The files with specified extension names in those directories will
#                   be automatically involved in compilation.
# LOCAL_CFLAGS_xxx.y:
#                 User-specified compiler flags for the xxx.y source file.
#                 YUNZ will automatically add extra common_cflags for include directories and macro
#                 definitions.
# CFLAGS_OVERRIDE_xxx.y:
#                 Overall compiler flags for the xxx.y source file. No any extra common_cflags will be
#                 involved for compling this file.
# MY_CFLAGS_*.y:  Compiler flags for all the source files with the extension y.
# LOCAL_EXCLUDE_FILES:  The files that are not included during compilation.
# LOCAL_OBJ_DIR:  The directory where object files are output.
# LOCAL_LDFLAGS:  Linker flags.
# ====================================================================================================
# LOCAL_MODULE:         The target name with path.
# LOCAL_MODULE_PRECONDITIONS: The dependencies of the target.
# ====================================================================================================
# LOCAL_C_EXTS:   The extension names for C source files.
# LOCAL_CPP_EXTS: The extension names for C++ source files.
# LOCAL_ASM_EXTS: The extension names for Assembly source files.
# LOCAL_OBJ_EXT:  The extension name of object files.
# LOCAL_D_EXT:    The extension name of dependency files.
# ====================================================================================================
# V:              Display verbose commands instead of short commands during
#                 the make process.
#-----------------------------------------------------------------------------------------------------#
# ymt_fast_build:  This project is independent of the makefile list. That is any
#                  change of the makefile list will not cause remaking of the project.
#######################################################################################################

ifndef ymt_include_once

ymt_include_once := 1

.PHONY: all clean distclean

#**************************************************************
# Basical functions
#**************************************************************
eq = $(if $(subst $1,,$2),,1)

do_ifeq  = $(if $(subst $1,,$2),,$3)
do_ifneq = $(if $(subst $1,,$2),$3)

define more_nl
========================= $(shell date +%N) =========================


$1
endef

ifeq (1,0)
exec = $(info $(call more_nl,$1))$(eval $1)
else
exec = $(eval $1)
endif
info2  = $(foreach i,$1,$(info $i = $($i)))
info3  = $(foreach i,$1,$(info $i = $(value $i)))

check_vars = $(foreach i,$1,$(if $($i),$(error Variable $i has been used! $($i))))
clear_vars = $(foreach i,$1,$(eval $i:=))

in_list = $(strip $(foreach i,$2,$(if $(subst $(strip $1),,$i),,$1)))#<>

unique = $(call check_vars,__ymt_v8)\
$(strip $(foreach i,$1,$(if $(call in_list,$i,$(__ymt_v8)),,$(eval __ymt_v8+=$i)))$(__ymt_v8))\
$(call clear_vars,__ymt_v8)

std_path = $(strip $(subst /./,/, \
  $(eval __ymt_v9 := $(subst ././,./,$(subst //,/,$(subst \\,/,$1)))) \
   $(if $(subst $(__ymt_v9),,$1),$(call std_path,$(__ymt_v9)),$1)))

get_path_list = $(call check_vars,__ymt_v1) \
  $(eval __ymt_v1 := $(call std_path,$1)) \
  $(call unique, $(call in_list, ./, $(__ymt_v1)) $(patsubst ./%,%,$(__ymt_v1))) \
  $(call clear_vars,__ymt_v1)

#--------------------------------------------------------------#
# Add a trailing LF character to the texts                     #
#  $1 -- The texts                                             #
#--------------------------------------------------------------#
define nl
$1

endef

TOP_MAKEFILES := $(MAKEFILE_LIST)
DEFAULT_C_EXTS   :=  c
DEFAULT_CXX_EXTS :=  cpp cc cxx
DEFAULT_ASM_EXTS :=  S s
system_vars := LOCAL_GCC_PREFIX LOCAL_CFLAGS LOCAL_CXXFLAGS LOCAL_LDFLAGS LOCAL_SRC_FILES LOCAL_C_INCLUDES LOCAL_MODULE \
  LOCAL_EXCLUDE_FILES LOCAL_LDLIBS LOCAL_OBJ_DIR LOCAL_MODULE_PRECONDITIONS EXTERNAL_DEPENDS LOCAL_REQUIRED_LIBS LOCAL_SRC_EXTS \
  LOCAL_C_EXTS LOCAL_CXX_EXTS LOCAL_ASM_EXTS MY_CMD_AS
CLEAR_VARS = $(call clear_vars, $(system_vars))

build_target = $(eval TARGET_TYPE := $1) $(eval X := $(LOCAL_MODULE)-) $(eval ymt_all_targets += $(LOCAL_MODULE)) \
  $(foreach i,$(DEFAULT_C_EXTS),$(eval action_$i := cc)) \
  $(foreach i,$(DEFAULT_CXX_EXTS),$(eval action_$i := cxx)) \
  $(foreach i,$(DEFAULT_ASM_EXTS),$(eval action_$i := as)) \
  $(call exec,include $(lastword $(TOP_MAKEFILES))) $(eval X:=)

BUILD_EXECUTABLE     = $(call build_target,EXE)
BUILD_SHARED_OBJECT  = $(call build_target,SO)
BUILD_STATIC_LIBRARY = $(call build_target,LIB)
BUILD_RAW_BINARY     = $(call build_target,BIN)

all: build-all
clean: clean-all
distclean: distclean-all
print-%:
	@echo $* = $($*)

.DEFAULT_GOAL = all

.PHONY: clean-all build-all distclean-all

#**************************************************************
#  include external configurations
#**************************************************************
$(foreach i,$(LOCAL_PROJECT_CONFIGS),$(eval DEPENDENT_MAKEFILES := $(TOP_MAKEFILES) $i) $(eval include $i))

build-all: $(foreach i,$(ymt_all_targets),$(i))
clean-all: $(foreach i,$(ymt_all_targets),clean-$(i))
distclean-all: $(foreach i,$(ymt_all_targets),distclean-$(i))

endif #ymt_include_once

#*******************************************************************
# PROJECT SPECIFIED PARTS
#*******************************************************************
ifneq ($(strip $(X)),)

$(if $(strip $(LOCAL_ASM_EXTS)),$(if $(strip $(MY_CMD_AS)),,$(error You must set MY_CMD_AS when you set LOCAL_ASM_EXTS!!)))

$(foreach i,$(LOCAL_C_EXTS),$(eval action_$i := cc)) \
 $(foreach i,$(LOCAL_CXX_EXTS),$(eval action_$i := cxx)) \
 $(foreach i,$(LOCAL_ASM_EXTS),$(eval action_$i := as))

#-------------------------------------------------------------------#
# Replace the pattern .. with !! in the path names in order that    #
# no directories are out of the object directory                    #
#  $1 -- The path names                                             #
#-------------------------------------------------------------------#
tr_objdir = $(subst /./,/,$(if $(objdir),$(subst ..,!!,$1),$1))

#--------------------------------------------------#
# Exclude user-specified files from source list.   #
#  $1 -- The sources list                          #
#--------------------------------------------------#
exclude = $(filter-out $(LOCAL_EXCLUDE_FILES),$1)

#---------------------------------------------#
# Replace the specified suffixes with $(O).   #
#  $1 -- The file names                       #
#  $2 -- The suffixes                         #
#---------------------------------------------#
get_object_names  = $(call tr_objdir,$(addprefix $(objdir),$(foreach i,$2,$(patsubst %.$i,%.$(O),$(filter %.$i,$1)))))

#--------------------------------------------------------------------#
# Set up one static pattern rule                                     #
#  $1 -- The static pattern rule                                     #
#  $2 -- cc or as
#--------------------------------------------------------------------#
define static_pattern_rules
$1
	$(call cmd,$(strip $2))

endef

#**************************************************************
#  Variables
#**************************************************************

# Quiet commands
quiet_cmd_cc        = @echo '  CC       $$< => $$@';
quiet_cmd_cxx       = @echo '  CXX      $$< => $$@';
quiet_cmd_as        = @echo '  AS       $$< => $$@';
quiet_cmd_link      = @echo '  LINK     $$@';
quiet_cmd_ar        = @echo '  AR       $$@';
quiet_cmd_mkdir     = @echo '  MKDIR    $$@';
quiet_cmd_objcopy   = @echo '  OBJCOPY  $$@';
quiet_cmd_clean     = @echo '  CLEAN    $(LOCAL_MODULE)';
quiet_cmd_distclean = @echo 'DISTCLEAN  $(LOCAL_MODULE)';

cmd = $(if $(strip $(V)),,$(quiet_cmd_$1))$(cmd_$1)

cmd_cc        = $(GCC) -I$$(dir $$<) $(subst subst_me,$(LOCAL_CFLAGS),$(common_cflags)) \
				$$(LOCAL_CFLAGS_$$<) -c -o $$@ $$<
cmd_cxx       = $(if $(strip $(LOCAL_CXXFLAGS)),$(GCC) -I$$(dir $$<) $(subst subst_me,$(LOCAL_CXXFLAGS),$(common_cflags)) \
                $$(LOCAL_CXXFLAGS_$$<) -c -o $$@ $$<,$(cmd_cc))
cmd_as        = $(if $(strip $(MY_CMD_AS)),$(value MY_CMD_AS),$(cmd_cc))
cmd_link      = $(LINK) $(ldflags) $(objects) $(LOCAL_LDLIBS) $(LOCAL_REQUIRED_LIBS) -o $$@
cmd_mkdir     = mkdir -p $$@
cmd_ar        = rm -f $$@ && $(AR) rcs $$@ $(objects)
cmd_objcopy   =	$(OBJCOPY) -O binary $< $$@
cmd_clean     = rm -rf $(filter-out ./,$(objdir)) $(LOCAL_MODULE) $(objects)
cmd_distclean = rm -f $(depends)

O := $(if $(LOCAL_OBJ_EXT),$(LOCAL_OBJ_EXT),o)
D := $(if $(LOCAL_D_EXT),$(LOCAL_D_EXT),d)

$(foreach i,$(LOCAL_C_EXTS) $(LOCAL_CXX_EXTS) $(LOCAL_ASM_EXTS),\
	$(if $(filter $i,$(LOCAL_SRC_EXTS)),,$(error Make sure "$i" included variable LOCAL_SRC_EXTS)))

# Return $1 if not empty, otherwise $2
xne = $(strip $(if $(strip $1),$1,$2))

LOCAL_SRC_EXTS := $(call unique,$(call xne,$(LOCAL_SRC_EXTS),\
 $(call xne,$(LOCAL_C_EXTS),$(DEFAULT_C_EXTS)) \
 $(call xne,$(LOCAL_CXX_EXTS),$(DEFAULT_CXX_EXTS)) \
 $(call xne,$(LOCAL_ASM_EXTS),$(DEFAULT_ASM_EXTS))))

source_patterns := $(foreach i, $(LOCAL_SRC_EXTS), %.$i)

objdir := $(strip $(LOCAL_OBJ_DIR))
objdir := $(patsubst ./%,%,$(if $(objdir),$(call std_path,$(objdir)/)))

## Combine compiler flags togather.
common_cflags   = $(foreach i,$(LOCAL_C_INCLUDES),-I$i) subst_me
ldflags = $(LOCAL_LDFLAGS)

#===============================================#
# Output file types:
#  EXE:  Executable
#  AR:   Static Library
#  SO:   Shared Object
#  DLL:  Dynamic Link Library
#  BIN:  Raw Binary
#===============================================#
TARGET_TYPE := $(strip $(TARGET_TYPE))
ifeq ($(filter $(TARGET_TYPE),SO DLL LIB EXE BIN),)
$(error Unknown TARGET_TYPE '$(TARGET_TYPE)')
endif

ifneq ($(filter DLL SO,$(TARGET_TYPE)),)
common_cflags   += -shared
ldflags += -shared
endif

common_cflags += -MMD -MF $$@.$(D) -MT $$@

#--------------------------------------------------------#
# Split apart source files and directories.
# The name of the directory must ends with a splash
#--------------------------------------------------------#
src_f = $(call get_path_list,$(filter $(source_patterns),$(LOCAL_SRC_FILES)))
src_d = $(call get_path_list,$(filter %/,$(LOCAL_SRC_FILES)))

sources = $(patsubst ./%, %, \
  $(foreach i, $(LOCAL_SRC_EXTS), \
    $(foreach j, $(src_d), $(wildcard $j*.$i))))
src_f := $(foreach i, $(src_f), $(if $(filter $i,$(sources)),,$i))
  $(foreach i, $(src_f), \
    $(foreach j, $(LOCAL_SRC_EXTS), $(if $(filter %.$j,$i),$(eval action-$i := $(action_$j)))))

#------------------------------------------------------------#
# sources: The list of all source files to be compiled       #
#------------------------------------------------------------#
sources := $(call exclude,$(sources) $(src_f))

GCC     := $(LOCAL_GCC_PREFIX)gcc
G++     := $(LOCAL_GCC_PREFIX)g++
AR      := $(LOCAL_GCC_PREFIX)ar
NM      := $(LOCAL_GCC_PREFIX)nm
OBJCOPY := $(LOCAL_GCC_PREFIX)objcopy
OBJDUMP := $(LOCAL_GCC_PREFIX)objdump
LINK    := $(if $(strip $(filter %.cpp %.cc %.cxx,$(sources))),$(G++),$(GCC))

ifeq ($(strip $(sources)),)
$(error Empty source list! Please check both LOCAL_SRC_FILES and LOCAL_SRC_EXTS are correctly set.)
endif

object_dirs = $(call tr_objdir,$(addprefix $(objdir),$(sort $(dir $(sources))))) $(dir $(LOCAL_MODULE))

#-----------------------------------------------------------#
# objects: The list of all object files to be created       #
#-----------------------------------------------------------#
objects = $(call get_object_names,$(sources),$(LOCAL_SRC_EXTS))

#-------------------------------------#
# The list of all dependent files     #
#-------------------------------------#
depends = $(foreach i,$(objects),$i.$(D))

depend_list = $(if $(strip $(ymt_fast_build)),$(DEPENDENT_MAKEFILES) $(EXTERNAL_DEPENDS))

define build_static_library
$(LOCAL_MODULE): $(LOCAL_MODULE_PRECONDITIONS) $(objects) | $(1)
	$(call cmd,ar)
endef

define build_raw_binary
target1  = $(basename $(LOCAL_MODULE)).elf
ldflags += -nodefaultlibs -nostdlib -nostartfiles
$(LOCAL_MODULE): $(target1)
	$(call cmd,objcopy)
endef

define build_elf
$(LOCAL_MODULE): $(LOCAL_MODULE_PRECONDITIONS) $(LOCAL_REQUIRED_LIBS) $(objects) | $(1)
	$(call cmd,link)
endef

ymt_build_LIB := build_static_library
ymt_build_SO  := build_elf
ymt_build_EXE := build_elf
ymt_build_BIN := build_raw_binary

#----------------------------------------------------#
# Construct Rules
#----------------------------------------------------#
ymt_dynamic_texts := \
$(call check_vars, __ymt_v1 __ymt_v2) \
  $(foreach i, $(src_d), \
    $(foreach j, $(LOCAL_SRC_EXTS), \
       $(eval __ymt_v1 := $(strip $(patsubst ./%, %, $(call exclude,$(wildcard $i*.$j))))) \
         $(if $(__ymt_v1), \
            $(eval __ymt_v2 = $(call get_object_names, $(__ymt_v1), $(LOCAL_SRC_EXTS))) \
            $(call static_pattern_rules, $(__ymt_v2) : \
            $(eval __ymt_v2 := $(if $(subst ./,,$i),$i)) \
            $(call tr_objdir, $(objdir)$(__ymt_v2)%.$(O)) : $(__ymt_v2)%.$j $(depend_list) | \
            $(call tr_objdir, $(objdir)$i),$(action_$j))))) \
  $(foreach i, $(src_f), \
    $(call static_pattern_rules, \
	  $(eval __ymt_v1 := $(call get_object_names,$i,$(LOCAL_SRC_EXTS))) \
      $(__ymt_v1): $i $(depend_list) | $(dir $(call tr_objdir, $(__ymt_v1))), $(action-$i))) \
$(call clear_vars, __ymt_v1 __ymt_v2)

ymt_dynamic_texts += \
  $(call nl, $(foreach i, $(object_dirs), $(if $(call in_list,$i,$(ymt_all_objdirs)),,$i)) : % : ; $(call cmd,mkdir))

$(eval ymt_all_objdirs += $(object_dirs))

ymt_dynamic_texts += \
$(call nl, \
  $(call $(ymt_build_$(TARGET_TYPE)), \
    $(subst ./,,$(call std_path,$(dir $(LOCAL_MODULE))))))

ymt_dynamic_texts += $(call nl, clean-$(LOCAL_MODULE): ; $(call cmd,clean))
ymt_dynamic_texts += $(call nl, distclean-$(LOCAL_MODULE): clean-$(LOCAL_MODULE) ; $(call cmd,distclean))

$(call exec, $(ymt_dynamic_texts))

sinclude $(if $(not_depend_makefile_list),,\
$(if $(call eq,all,$(if $(MAKECMDGOALS),$(MAKECMDGOALS),$(.DEFAULT_GOAL))),$(foreach i,$(objects),$i.$(D))))

endif # CORE_BUILD_RULES

