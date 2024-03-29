import gzip

import click

from collections import defaultdict
from typing import Dict, List, Optional

from pysam import AlignedSegment, AlignmentFile

from svtoolbox.exceptions import InfoFieldNotFound, SVToolBoxException
from svtoolbox.parser import parse_vcf
from svtoolbox.validation import check_contig_support


@click.group()
def client():
    pass


@client.command()
@click.option("--vcf", type=click.Path(exists=True), required=True)
@click.option("--include_fields", type=str, required=False)
def create_bedpe(vcf: str, include_fields: Optional[str] = None) -> None:
    with gzip.open(vcf, "rt") as stream:
        for variant in parse_vcf(stream).values():
            print(
                variant.to_bedpe(
                    include_fields=include_fields.split(",") if include_fields else None
                )
            )


@client.command()
@click.option("--vcf", type=click.Path(exists=True), required=True)
def create_contigs_fastq(vcf: str) -> None:
    with gzip.open(vcf, "rt") as stream:
        for variant in parse_vcf(stream).values():
            try:
                contig = str(variant.get_info("CONTIG"))
                print("\n".join([f"@{variant.id}", contig, "+", "I" * len(contig)]))
            except InfoFieldNotFound:
                pass


@client.command()
@click.option("--vcf", type=click.Path(exists=True), required=True)
@click.option("--bam", type=click.Path(exists=True), required=True)
def validate_variants(vcf: str, bam: str) -> None:
    alignments: Dict[str, List[AlignedSegment]] = defaultdict(list)
    for alignment in AlignmentFile(bam, "rb"):
        if alignment.query_name is None:
            raise SVToolBoxException("Missing query name in alignment")
        alignments[alignment.query_name].append(alignment)

    with gzip.open(vcf, "rt") as stream:
        variants = parse_vcf(stream)

    added_info_field = False
    with gzip.open(vcf, "rt") as f:
        for line in f.read().splitlines():
            # This is a header line
            if line.startswith("#"):
                # Add the SUPPORTED INFO field definition together with
                # the definitons of the other INFO fields.
                if line.startswith("##INFO") and not added_info_field:
                    print(
                        '##INFO=<ID=SUPPORTED,Number=0,Type=Flag,Description="Supported by contig breakpoints">'
                    )
                    added_info_field = True
                # Keep all existing header lines
                print(line)
                continue
            # We have reached the end of the header
            break

    for variant in variants.values():
        # Add SUPPORTED flag if the variant is supported by contig breakpoints
        if check_contig_support(variant=variant, alignments=alignments[variant.id]):
            variant.set_info(key="SUPPORTED", value=True)
        print(variant)


def run():
    client()
