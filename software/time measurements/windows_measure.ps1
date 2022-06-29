1..100 | % {Measure-Command {python ../ping_example.py} | Out-File -FilePath .\measurement.txt -append}
#for run in {1..100}; do \time -f %e python3 ../ping_example.py ; done
