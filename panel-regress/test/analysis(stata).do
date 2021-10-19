#表4-2
import delimited /Users/yasuta/Documents/GitHub/Python/Tasks/20200723/analysis.csv
asdoc summarize debt1 debt2 equity1 equity2 fl ol sl ll q cf ca cycle scale roa, detail

#表4-3
import delimited /Users/yasuta/Documents/GitHub/Python/Tasks/20200723/analysis.csv
asdoc correlate debt1 debt2 equity1 equity2 fl ol sl ll q cf ca cycle scale roa

#表4-4
import delimited /Users/yasuta/Documents/GitHub/Python/Tasks/20200723/analysis.csv
egen id=group(company)
xtset id time, quarterly
asdoc xtreg debt1 q cf ca, fe nest
asdoc xtreg equity1 q cf ca, fe nest
asdoc xtreg debt1 q cf ca cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg equity1 q cf ca cycleq cyclecf cycleca roa scale, fe nest

#表4-5
import delimited /Users/yasuta/Documents/GitHub/Python/Tasks/20200723/analysis.csv
egen id=group(company)
xtset id time, quarterly
asdoc xtreg fl q cf ca, fe nest
asdoc xtreg ol q cf ca, fe nest
asdoc xtreg fl q cf ca cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg ol q cf ca cycleq cyclecf cycleca roa scale, fe nest

#表4-6
import delimited /Users/yasuta/Documents/GitHub/Python/Tasks/20200723/analysis.csv
egen id=group(company)
xtset id time, quarterly
asdoc xtreg sl q cf ca, fe nest
asdoc xtreg ll q cf ca, fe nest
asdoc xtreg sl q cf ca cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg ll q cf ca cycleq cyclecf cycleca roa scale, fe nest

#表4-7
import delimited /Users/yasuta/Documents/GitHub/Python/Tasks/20200723/analysis.csv
egen id=group(company)
xtset id time, quarterly
asdoc xtreg debt1 q cf ca cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg equity1 q cf ca cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg debt1 q cf ca cycle cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg equity1 q cf ca cycle cycleq cyclecf cycleca roa scale, fe nest

表4-14
import delimited /Users/yasuta/Documents/GitHub/Python/Tasks/20200723/analysis.csv
egen id=group(company)
xtset id time, quarterly
asdoc xtreg debt1 q cf ca cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg equity1 q cf ca cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg debt2 q cf ca cycleq cyclecf cycleca roa scale, fe nest
asdoc xtreg equity2 q cf ca cycleq cyclecf cycleca roa scale, fe nest

表4-15
import delimited /Users/yasuta/Documents/GitHub/Python/Tasks/20200723/analysis.csv
egen id=group(company)
xtset id time, quarterly
asdoc xtreg debt1 q cf ca cycleq cyclecf cycleca roa scale, be nest
asdoc xtreg equity1 q cf ca cycleq cyclecf cycleca roa scale, be nest
asdoc xtreg debt2 q cf ca cycleq cyclecf cycleca roa scale, be nest
asdoc xtreg equity2 q cf ca cycleq cyclecf cycleca roa scale, be nest
