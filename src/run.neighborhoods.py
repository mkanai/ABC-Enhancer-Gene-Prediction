import argparse
import os
from neighborhoods import *
from subprocess import getoutput

def parseargs(required_args=True):
    class formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
        pass

    epilog = ("")
    parser = argparse.ArgumentParser(description='Run neighborhood for a given cell type',
                                     epilog=epilog,
                                     formatter_class=formatter)
    readable = argparse.FileType('r')
    
    #parser.add_argument('--params_file', required=required_args, help="File listing feature files for each cell type.")
    parser.add_argument('--candidate_enhancer_regions', required=required_args, help="Bed file containing candidate_enhancer_regions")
    parser.add_argument('--outdir', required=required_args, help="Directory to write Neighborhood files to.")
    
    #parser.add_argument('--genome', required=required_args, help="File listing genome annotations for each species/build")
    parser.add_argument('--genes', required=required_args, help="bed file with gene annotations. Must be in bed-6 format")
    parser.add_argument('--gene_name_annotations', default="symbol,refseq", help="Comma delimited string of names corresponding to the gene identifiers present in the name field of the gene annotation bed file")
    parser.add_argument('--primary_gene_identifier', default="symbol", help="Primary identifier used to identify genes. Must be present in gene_name_annotations. The primary identifier must be unique")
    parser.add_argument('--ubiquitously_expressed_genes', default=None, help="File listing ubiquitously expressed genes. These will be flagged by the model, but this annotation does not affect model predictions")

    parser.add_argument('--chrom_sizes', required=required_args, help="Genome file listing chromosome sizes. Also requires associated .bed file")

    parser.add_argument('--H3K27ac', required=required_args, default=None, help="Comma delimited string of H3K27ac .bam files")
    parser.add_argument('--DHS', default=None, help="Comma delimited string of DHS .bam files. Either ATAC or DHS must be provided")
    parser.add_argument('--ATAC', default=None, help="Comma delimited string of ATAC .bam files. Either ATAC or DHS must be provided")
    parser.add_argument('--default_accessibility_feature', default=None, help="If both ATAC and DHS are provided, this flag must be set to either 'DHS' or 'ATAC' signifying which datatype to use in computing activity")
    parser.add_argument('--expression_table', default=None, help="Comma delimited string of gene expression files")

    #Other
    parser.add_argument('--tss_slop_for_class_assignment', default=500, type=int, help="Consider an element a promoter if it is within this many bp of a tss")
    parser.add_argument('--skip_rpkm_quantile', action="store_true", help="Do not compute RPKM and quantiles in EnhancerList.txt")
    parser.add_argument('--use_secondary_counting_method', action="store_true", help="Use a slightly slower way to count bam over bed. Also requires more memory. But is more portable across systems")
    parser.add_argument('--cellType', help="Name of cell type")

    # replace textio wrapper returned by argparse with actual filename
    args = parser.parse_args()
    for name, val in vars(args).items():
        if hasattr(val, 'name'):
            setattr(args, name, val.name)
    print(args)
    return args

def processCellType(args):
    params = parse_params_file(args)

    os.makedirs(args.outdir, exist_ok=True)

    #Setup Genes
    genes = load_genes(file = args.genes, 
                        ue_file = args.ubiquitously_expressed_genes,
                        chrom_sizes = args.chrom_sizes,
                        outdir = args.outdir, 
                        expression_table_list = params["expression_table"], 
                        gene_id_names = args.gene_name_annotations, 
                        primary_id = args.primary_gene_identifier,
                        cellType = args.cellType)
    annotate_genes_with_features(genes = genes, 
                                    genome_sizes = args.chrom_sizes, 
                                    use_fast_count = (not args.use_secondary_counting_method),
                                    default_accessibility_feature = params['default_accessibility_feature'],
                                    features = params['features'],
                                    outdir = args.outdir)

    #Setup Candidate Enhancers
    load_enhancers(genes=genes, 
                    genome_sizes=args.chrom_sizes, 
                    candidate_peaks=args.candidate_enhancer_regions, 
                    skip_rpkm_quantile=args.skip_rpkm_quantile, 
                    #cellType=cellType, 
                    tss_slop_for_class_assignment=args.tss_slop_for_class_assignment,
                    use_fast_count = (not args.use_secondary_counting_method),
                    default_accessibility_feature = params['default_accessibility_feature'],
                    features = params['features'],
                    cellType = args.cellType,
                    outdir = args.outdir)

def main(args):
    processCellType(args)

if __name__ == '__main__':
    args = parseargs()
    main(args)