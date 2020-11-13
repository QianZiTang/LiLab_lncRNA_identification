from HTSeq import GFF_Reader
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '--gtf',
    help='gtf file',
    required=True)
parser.add_argument(
    '--id_file',
    help='Output directory.',
    required=True)
parser.add_argument(
    '--flag',
    help='extract "ex" or delete "de" gtf record in id_file.',
    choices=['ex', 'de'],
    default='ex')
parser.add_argument(
    '--id_type',
    help='id type.',
    choices=['gene', 'transcript'],
    default='transcript')
parser.add_argument(
    '--output',
    help='output gtf file.',
    required=True)
args = parser.parse_args()

id_dict = {}
with open(args.id_file, 'r') as id_file_info:
    for eachline in id_file_info:
        eachline = eachline.strip()
        if eachline:
            id_dict[eachline] = 1

output_info = open(args.output, 'w')

attr_flag = '{i}_id'.format(i=args.id_type)
for eachline in GFF_Reader(args.gtf):
    if args.flag == 'ex':
        if eachline.attr[attr_flag] in id_dict:
            output_info.write("%s;\n" % eachline.get_gff_line().strip())
    else:
        if eachline.attr[attr_flag] not in id_dict:
            output_info.write("%s;\n" % eachline.get_gff_line().strip())
output_info.close()
