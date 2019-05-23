# Halide note

### learn from: https://blog.csdn.net/luzhanbo207/article/details/78689444

### Func, Var, Expr

Func用Var表达出后只是在内存中记录，需要调用realize函数：Buffer\<int\>output = gradient.realize(8,8)

### [3] Debug1
加入export HL_DEBUG_CODEGEN=(1/2) 运行执行文件后可显示pipeline和compile过程，但是不知道怎么看？
还可以在代码中加入生成html来查看的代码

### [4] Debug2
[Func].trace_stores() 跟踪所有的函数计算值; [Func].parallel([Var])：指示并行，对算法进行调度：此时输出会out of order，因为每行的计算可能位于不同线程; 若只关注表达式的某个条目，可以在这个条目上加上print函数，也可以对Expr使用：Expr e = cos(y),e = print(e,"any comment",y)  
expr = print_when(bool_expr, expr, context):如果 bool_expr == ture: 返回expr，打印context内容;否则只返回expr

### [5] 调度
https://blog.csdn.net/luzhanbo207/article/details/78710831  
默认顺序：列（x）优先，[x,y]:[0,0],[1,0],[2,0]...... 
#### Reorder   
[Func].reorder(y,x)：行（y）优先   [Func].print_loop_nest()可以查看循环顺序;    
#### Split
[Func].split(x, x_outer, x_inner, 2);  split将x拆成x_outer,x_inner, 内循环的长度为2     
(```)
    Pseudo-code for the schedule:
    Injecting realization of { gradient_split }
    produce gradient_split:
    for y:
        for x.x_outer:  
        for x.x_inner in [0, 1]:
            gradient_split(...) = ...  
(```)
#### Fuse 
[Var] fused; [Func].fuse(x, y, fused);      
#### Tile
[Var] x_outer, x_inner, y_outer, y_inner;   
[Func].split(x, x_outer, x_inner, 4);   
[Func].split(y, y_outer, y_inner, 4);   
[Func].reorder(x_inner, y_inner, x_outer, y_outer);     
与 [Func].tile(x, y, x_outer, y_outer, x_inner, y_inner, 4, 4);
#### Vectorize
将内层循环向量化计算    
Var x_outer, x_inner; 
gradient.split(x, x_outer, x_inner, 4); 
gradient.vectorize(x_inner);    

上述过程有更简单的形式
gradient.vectorize(x, 4);   
等价于
gradient.split(x, x, x_inner, 4);
gradient.vectorize(x_inner);    
这里我们重用了x，将它当作外循环变量，稍后的调度将x当作外循环(x_outer)来进行调度s
#### Loop Unrolling
和向量化类似，先将数据划分，然后将内层循环铺平  
Var x_outer, x_inner;   
gradient.split(x, x_outer, x_inner, 2);
gradient.unroll(x_inner);

The shorthand for this is:  
gradient.unroll(x, 2);
#### Splitting by factors that don't divide the extent
当原来图像尺寸不能整除划分的小矩形尺寸时，最后的一行或者一列的tile在边界处会出现重复计算的现象;由于Halide函数没有边缘效应，因此计算多次并不会产生副作用。
#### Fuse + Tile + Parallelize
tile层面的调度是乱序的，但是在每一个tile内部，是行优先的计算顺序    
Var x_outer, y_outer, x_inner, y_inner, tile_index;  
gradient.tile(x, y, x_outer, y_outer, x_inner, y_inner, 4, 4);  
gradient.fuse(x_outer, y_outer, tile_index);    
gradient.parallel(tile_index);  

// 每个调度函数返回的是引用类型，因此可以按如下方式用点号连接起多次调用 
// gradient  
//     .tile(x, y, x_outer, y_outer, x_inner, y_inner, 2, 2)    
//     .fuse(x_outer, y_outer, tile_index)  
//     .parallel(tile_index);   

### [6]在指定区域上执行函数
Buffer<int> shifted(5,7)
shifted.set_min(100,50) //指定计算区域的起始坐标（左上角）
gradient.realize(shifted)

### [7]多阶段流水线
如果超出了输入图像的边界可以编译通过（很慢），执行时候还会报错。    
采用Expr clamped_x = clamp(x,0,input.width()-1) ； Expr clamped_y = clamp(y,0,input.height()-1) clamped(x,y,c) = input(clamped_x,clamped_y,c)；

Func之间可以套用，表示逐个使用  
[Func2] = cast<uint8_t>([Func1](x,y,c))

### [8] 多阶段流水线调度
default：两个Func套接，实际上只会调用内部的Func，不会存储 -- inline schedule  
producer（内部Func）.compute_root() 使得内部Func会先存储，再被外层Func调用     

这里的a.compute_at(b, c)理解为在b的c循环里插入a的计算
producer.compute_at(consumer, y);   
producer.store_root().compute_at(comsumer,y) 缓存所有数据  

### [9] Multi-pass Funcs, update definitions, reductions
[func].trace_loads()  [func].trace_stores()可追踪load和store的情况  
RDom 似乎能完成循环迭代的功能, RDom(0,5)表示一个x从0到5（不包括5）的reduction domain。对于RDom r(x_start,x_len,y_start,y_len)可以通过调用r.x和r.y使用

schedule update steps: 之前的schedule API只针对pure function（不包括后来的更新定义）。对于更新定义的调度：f.update(0).vectorize(x,4); f.update(1).parallel(y)...... 

Consumer + producer + update: 基本是一样的操作 .compute_at     

Halide.h 中有许多reduction helpers: 常用的有 sum(r+x) ,这个表达式其实自动创建了一个匿名Func。而Func f1 = sum(r+x) * 7，这个f1就是pure function      
其他reduction helpers: maximum, minimum, argmin, argmax, mutiple    

### [10] AOT(ahead-of-time) compilation 提前编译
利用compile_to_static_library()函数，可生成静态链接库和头文件。

### [11] 跨平台编译
编译后执行不了？  已放弃（核心已转储）  
通过[Func].compile_to_file()函数可以生成针对不同Target的object文件。Target通过参数输入该函数中。    

### [12] Using the GPU
在GPU上有一些特定的函数可以用来Schedule 

### [13] Tuples 元组
1. 可以通过Halide::select()函数实现 multi-value的Func。select()类似C的switch   
2. Func数组实现多值函数
3. 将Func定义为Tuple instead of Expr。Tuple的每一个表达式可以有不同的数据类型
```
Func multi_valued;
multi_valued(x, y) = Tuple(x + y, sin(x * y)); //Can Also: multi_valued_2(x, y) = {x + y, sin(x*y)}
Realization r = multi_valued.realize(80, 60);
```
Realization r相当于一个buffer向量对象，且每个buffer可以有不同的数据类型 

调用时也需要以索引方式处理：
```
 Expr integer_part = multi_valued_2(x, y)[0];
 Expr floating_part = multi_valued_2(x, y)[1];
 Func consumer;
 consumer(x, y) = {integer_part + 10, floating_part + 10.0f};
```
在RDom 约减操作中Tuple很好用    

可以通过Tuple来帮助构建新的数据类型，例如复数   

### [14] Halide Type System
Expr也有Type。可通过cast函数转换Type    
Func可以调用 [func].output_types()[0]得到其Type. 对于多值函数[0]换成[n] 
Halide的类型转化规则:...... 
Type的使用主要在于：可以在程序中runtime改变Type，可以当做一个变量来测试的感觉   

### [15] Generators 生成器 (没太搞懂,最后该怎么执行？)
通过继承Halide::Generator<...>得到Generator类，实现自己定义的pipeline   
GeneratorParam<...> xxx 来定义生成器变量，这会影响Halide pipeline   
自适应地选择一个合适的因子进行向量化：
```
output.vectorize(x, natural_vector_size(output.type()));
```
注册Generator:  
```
HALIDE_REGISTER_GENERATOR(MySecondGenerator, my_second_generator)
```
Conclusion: 结构化生成器编写格式
```
class MyGenerator : public Halide::Generator<MyGenerator>
{
    Input a, b; //...
    Output c, d; //...
    GeneratorParam<T> ...

    void generate()
    {

    }
};
HALIDE_REGIRTER_GENERATOR(MyGenerator, my_generator)
```

#### 生成Generator可执行文件后，实现编译
```
./lesson_15_generate \
    -g my_first_generator \
    -f my_first_generator_win32 \
    -o . \
    target=x86-32-windows
```
-g:生成器名，-o:目录, -f:制定生成的函数名, target:指定编译的目标平台, -e 生成的文件的类型   

若Generator带参数：(在runtime设置)
```
/lesson_15_generate -g my_second_generator -f my_second_generator_1 -o . \
target=host parallel=false scale=3.0 rotation=ccw output.type=uint16
```

### [16] RGB images and memory layouts: 没有运行成功
[15]的应用：Param设置为不同的memory Layout. 根据不同的Memory Layout适合不同的schedule   
[Func].specialize([condition])可以通过runtime的设定来调整[Func]的schedule   
set_stride(), set_extent()  

### [17] Reductions over non-rectangular domains 提供一个在任意限定条件区域运算的表达方式
[9]中的RDom只能是矩形区域，如果想在自定区域中迭代需要RDom::where    
```
RDom r(0,7,0,7) %区域需要包含之后的自定区域
r.where((r.x - 3)*(r.x - 3) + (r.y - 3)*(r.y - 3) <= 10);
circle(r.x, r.y) *= 2;
Buffer<int> halide_result = circle.realize(7, 7);
```
区域的限制不止可以通过r.x,r.y来约束，也可以通过与其相关的[Func]：
```
Func f("f"), g("g");
Var x("x"), y("y");
f(x, y) = 2 * x + y;
g(x, y) = x + y;

RDom r1(0, 5, 0, 5);
r1.where(f(r1.x, r1.y) >= 4);
r1.where(f(r1.x, r1.y) <= 7);
f(r1.x, r1.y) /= 10;
```
### [18] Factoring an associative reduction using rfactor
rfactor将有依赖更新区域分解成一系列的小切片，对小切片分别进行处理后，将所有结果汇总起来，得到整体的结果 
```
Func intermediate = histogram.update().rfactor({{rx_outer, u}, {ry_outer, v}});
```

### [19] Wrapper Funcs 包裹函数
关于使用Func::in和ImageParam::in     
在f和g之间插入一个新的函数，插入的新函数可以单独调度    
```
Func f_in_g = f.in(g);
f_in_g.compute_root();
```

### [20] Cloning Funcs 克隆方程
Func::clone_in对函数进行克隆，且克隆可以单独调度    

### [21] Auto-Scheduler 自动调度器





