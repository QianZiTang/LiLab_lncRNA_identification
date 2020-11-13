import pandas as pd
from collections import Counter
import click
from scipy import stats


@click.command()
@click.option(
    '-c',
    '--coding_pfam',
    type=click.Path(exists=True),
    required=True,
    help='pfam prediction for coding sequences.')
@click.option(
    '-n',
    '--noncoding_pfam',
    type=click.Path(exists=True),
    required=True,
    help='pfam prediction for noncoding sequences.')
@click.option(
    '-p',
    '--pfam_hit',
    type=click.File('w'),
    required=True,
    help='valid Pfam domains in transcribed regions')
def main(coding_pfam, noncoding_pfam, pfam_hit):
    cd_df = pd.read_csv(coding_pfam, header=None, delim_whitespace=True,
                        skip_blank_lines=True, comment="#")
    cd_total = len(cd_df)
    cd_count = Counter(cd_df.loc[:, 5])
    nc_df = pd.read_csv(noncoding_pfam, header=None, delim_whitespace=True,
                        skip_blank_lines=True, comment="#")
    nc_total = len(nc_df)
    nc_count = Counter(nc_df.loc[:, 5])
    for each_hit in cd_count:
        if each_hit in nc_count:
            cd_hit, cd_nohit = cd_count[
                each_hit], cd_total - cd_count[each_hit]
            nc_hit, nc_nohit = nc_count[
                each_hit], nc_total - nc_count[each_hit]
            oddsratio, pvalue = stats.fisher_exact([[cd_hit, cd_nohit],
                                                    [nc_hit, nc_nohit]])
            if oddsratio > 10 and pvalue < 0.05:
                pfam_hit.write('{h}\n'.format(h=each_hit))
        else:
            pfam_hit.write('{h}\n'.format(h=each_hit))


if __name__ == '__main__':
    main()
