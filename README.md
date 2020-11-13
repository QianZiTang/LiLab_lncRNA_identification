# LiLab_lncRNA_identification

## PARTI
codes for de novo transcriptome assembly and novel lncRNA and TUCP identification

## 1. System requirements

- centOS 7
- python 2.7.5
- STAR 2.5.3a
- cufflinks v2.2.1
- AssemblyLine 0.2.0
- TACO v0.7.3
- EMBOSS 6.5.7
- CPC2 0.1
- pfam_scan.pl 1.5
- bedtools v2.27.1
- CIRCexplorer2 2.3.2
- python packages: HTSeq 0.9.1, pandas 0.22.0, click 6.7, scipy 1.1.0

## 2. Installation guide

No installation needed
Directly run the python scripts

##  3. Instructions for use

### mapping 

```
#mapping
STAR \
    --genomeDir star_index \
    --readFilesIn sample.R1.fq.gz sample.R2.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix bam/sample/ \
    --runThreadN 16 \
    --outSAMtype BAM SortedByCoordinate \
    --outFilterType BySJout \
    --outFilterMultimapNmax 20 \
    --alignSJoverhangMin 8 \
    --alignSJDBoverhangMin 1 \
    --outFilterMismatchNmax 999 \
    --alignIntronMin 20 \
    --alignIntronMax 1000000 \
    --alignMatesGapMax 1000000 \
    --chimSegmentMin 10
```

### assembly
```
## cufflink assembly
cufflinks -g gene.gtf --library-type fr-firststrand -o gtf/sample bam/sample/Aligned.sortedByCoord.out.bam
```

### AssemblyLine to filter background transcripts
```
# AssemblyLine to filter background transcripts
aggregate_transcripts.py -o assemblyLine_dir gene.gtf gtf.config
annotate_transcripts.py assemblyLine_dir
assemblyLine_dir assemblyLine_dir
```
### TACO to merge and compare to ref
```
taco_run \
    --filter-min-expr 0.1 \
    --isoform-frac 0.1 \
    --path-kmax 20 \
    --max-paths 20 \
    --filter-min-length 250 \
    -o taco_merge
    filter.gtf.config

taco_refcomp \
    -r gene.gtf \
    -t taco_merge/assembly.gtf \
    -o taco_merge
```
### coding potential
```
## prepare: extract lncRNA candidates gtf/fa/orf from TACO merged gtf

python get_gtf_by_id.py \
    --gtf assembly.refcomp.gtf \
    --id_file lncrna.candidates.list \
    --output lncrna.candidates.gtf

gffread lncrna.candidates.gtf -g genome.fa -w lncrna.candidates.fa

### EMBOSS: getorf
getorf -noreverse -sequence lncrna.candidates.fa -outseq lncrna.candidates.orf.fa

## CPC2
CPC2.py -i lncrna.candidates.fa -o cpc.out
awk '$7=="coding"' cpc.out | cut -f1 > cpc.coding.list

## PFAM

### validate coding region pfam domains

#### coding region pfam domains
pfam_scan.pl -fasta pep.fa -o coding.pfam.out

#### noding coding region pfam domains
bedtools shuffle -seed 1 -i mRNA.cds.bed -g chr.size -excl coding.region.gene.bed > random.nc.region.bed
bedtools getfasta -fi genome.fa -bed random.nc.region.bed -fo random.nc.region.fa -name
getorf -sequence random.nc.region.fa -outseq random.nc.region.orf.fa
pfam_scan.pl -fasta random.nc.region.orf.fa -o nc.region.pfam.out

#### extract valid coding region pfam domains (Fisher’s Exact Test odds ratio less than 10.0 or p-value greater than 0.05 to be artifacts)
python valid_coding_pfam_domains.py --coding_pfam coding.pfam.out --noncoding_pfam nc.region.pfam.out --pfam_hit valid.coding.pfam.domains

### lncRNA candidates pfam analysis
pfam_scan.pl -fasta lncrna.candidates.orf.fa -o pfam.out
python valid_pfam_hits.py \
    --pfam_id valid.coding.pfam.domains
    pfam.out \
    pfam.coding.list \


### final lncRNA sets
cat pfam.coding.list cpc.coding.list| sort -u > coding.potential.transcripts.list
python get_gtf_by_id.py \
    --gtf lncrna.candidates.gtf \
    --id_file coding.potential.transcripts.list \
    --flag de  \
    --output lncrna.gtf

# circRNA identify

CIRCexplorer2 parse -t STAR -b sample.back_spliced_junction.bed sample.Chimeric.out.junction
CIRCexplorer2 annotate -r gene.reflat -g genome.fa -b sample.back_spliced_junction.bed -o sample.circularRNA.txt
```
