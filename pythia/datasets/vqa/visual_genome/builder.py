
import os
import shutil

from pythia.common.registry import registry
from pythia.datasets.vqa.vqa2.builder import VQA2Builder
from pythia.datasets.vqa.visual_genome.dataset import VisualGenomeDataset
from pythia.utils.general import download_file, extract_file, get_pythia_root
from pythia.common.constants import VISUAL_GENOME_CONSTS


@registry.register_builder("visual_genome")
class VisualGenomeBuilder(VQA2Builder):
    def __init__(self):
        super().__init__()
        self.dataset_name = "visual_genome"
        self.dataset_proper_name = "Visual Genome"
        self.dataset_class = VisualGenomeDataset
        self.writer = registry.get("writer")

    def _build(self, dataset_type, config):
        self._dataset_type = dataset_type
        self._config = config
        data_folder = os.path.join(get_pythia_root(), self._config.data_root_dir)

        # Since the imdb tar file contains all of the sets, we won't download them
        # except in case of train
        if self._dataset_type != "train":
            return

        self._download_and_extract_imdb(data_folder)
        self._download_and_extract_features(data_folder)

    def _download_and_extract_imdb(self, data_folder):
        download_folder = os.path.join(data_folder, "imdb")
        vocab_folder = os.path.join(data_folder, "vocabs")
        vocab_file = os.path.join(vocab_folder, VISUAL_GENOME_CONSTS["synset_file"])
        os.makedirs(vocab_folder, exist_ok=True)

        self._download_and_extract(
            "vocabs", VISUAL_GENOME_CONSTS["vocabs"], data_folder
        )
        extraction_folder = self._download_and_extract(
            "imdb_url", VISUAL_GENOME_CONSTS["imdb_url"], download_folder
        )

        if not os.path.exists(vocab_file):
            shutil.move(
                os.path.join(extraction_folder, VISUAL_GENOME_CONSTS["synset_file"]),
                vocab_file
            )

    def _download_and_extract_features(self, data_folder):
        self._download_and_extract(
            "features_url", VISUAL_GENOME_CONSTS["features_url"], data_folder
        )

    def _download_and_extract(self, key, url, download_folder):
        file_type = key.split("_")[0]
        os.makedirs(download_folder, exist_ok=True)
        local_filename = url.split("/")[-1]
        extraction_folder = os.path.join(download_folder, local_filename.split(".")[0])
        local_filename = os.path.join(download_folder, local_filename)

        if os.path.exists(local_filename) or \
            (os.path.exists(extraction_folder) and len(os.listdir(extraction_folder))) != 0:
            self.writer.write(
                "{} {} already present. Skipping download.".format(
                    self.dataset_proper_name, file_type
                )
            )
            return extraction_folder


        self.writer.write("Downloading the {} {} now.".format(
            self.dataset_proper_name, file_type)
        )
        download_file(url, output_dir=download_folder)

        self.writer.write(
            "Extracting the {} {} now. This may take time".format(
                self.dataset_proper_name, file_type
            )
        )
        extract_file(local_filename, output_dir=download_folder)

        return extraction_folder


