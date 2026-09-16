# QE Practice 01: SCF, E(V), and start of relaxation

Цель занятия: запустить SCF для Si, получить одну точку E(a), собрать общий график E(V), затем запустить relax для слегка смещённой структуры.

Минимальная команда запуска:

```bash
mpirun -np 2 pw.x -in inputs/si_diamond_scf.in > si_diamond_scf.out
```

Перед занятием проверьте, что файл псевдопотенциала Si лежит в `pseudo/` и его имя совпадает с `ATOMIC_SPECIES` во входных файлах.
