# Makefile
https://blog.csdn.net/weixin_38391755/article/details/80380786

target... : prerequisites ...
(tab)    command

# symbol
@ 在命令前：make时不打印这条命令

## 自动化变量
$@  表示规则中的目标文件集。在模式规则中，如果有多个目标，那么，"$@"就是匹配于目标中模式定义的集合。

$%  仅当目标是函数库文件中，表示规则中的目标成员名。例如，如果一个目标是"foo.a(bar.o)"，那么，"$%"就是"bar.o"，"$@"就是"foo.a"。如果目标不是函数库文件（Unix下是[.a]，Windows下是[.lib]），那么，其值为空。

$<   依赖目标中的第一个目标名字。如果依赖目标是以模式（即"%"）定义的，那么"$<"将是符合模式的一系列的文件集。注意，其是一个一个取出来的。

$?   所有比目标新的依赖目标的集合。以空格分隔。

$^   所有的依赖目标的集合。以空格分隔。如果在依赖目标中有多个重复的，那个这个变量会去除重复的依赖目标，只保留一份。

## apps
CXX ?= g++
GXX ?= g++

BIN ?= bin
HL_TARGET ?= host
GENERATOR_BIN ?= bin/host
GENERATOR_OUTPUTS ?= static_library,h,registration,stmt,assembly
GENERATOR_DEPS ?= $(LIB_HALIDE) $(HALIDE_DISTRIB_PATH)/include/Halide.h $(HALIDE_DISTRIB_PATH)/tools/GenGen.cpp

### apps/blur

```
jiajieli@u17-jiajieli:~/Halide/apps/blur$ make test
bin/host/test
times: 0.326238 0.033716 0.005133
```

