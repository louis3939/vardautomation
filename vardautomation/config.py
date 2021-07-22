"""Automation module"""

__all__ = ['FileInfo']

import sys
from operator import attrgetter
from pprint import pformat
from typing import List, Optional, Sequence, Union, cast

import vapoursynth as vs
from pymediainfo import MediaInfo
from vardefunc.util import adjust_clip_frames

from .presets import Preset, PresetGeneric
from .types import AnyPath
from .types import DuplicateFrame as DF
from .types import Trim, VPSIdx
from .vpathlib import VPath

core = vs.core


class FileInfo:
    """File info object"""
    path: VPath
    path_without_ext: VPath
    work_filename: str

    idx: Optional[VPSIdx]
    preset: List[Preset]

    name: str

    workdir: VPath

    a_src: Optional[VPath]
    a_src_cut: Optional[VPath]
    a_enc_cut: Optional[VPath]
    chapter: Optional[VPath]

    clip: vs.VideoNode
    _trims_or_dfs: Union[List[Union[Trim, DF]], Trim, None]
    clip_cut: vs.VideoNode

    name_clip_output: VPath
    name_file_final: VPath

    name_clip_output_lossless: VPath
    do_lossless: bool

    qpfile: VPath
    do_qpfile: bool


    def __init__(
        self, path: AnyPath, /,
        trims_or_dfs: Union[List[Union[Trim, DF]], Trim, None] = None, *,
        idx: Optional[VPSIdx] = None,
        preset: Union[Sequence[Preset], Preset] = PresetGeneric,
        workdir: AnyPath = VPath().cwd()
    ) -> None:
        """Helper which allows to store the data related to your file to be encoded

        Args:
            path (AnyPath):
                Path to your source file.

            trims_or_dfs (Union[List[Union[Trim, DF]], Trim, None], optional):
                Adjust the clip length by trimming or duplicating frames. Python slicing.
                Defaults to None.

            idx (Optional[Callable[[str], vs.VideoNode]], optional):
                Indexer used to index the video track.
                Defaults to None.

            preset (Union[Sequence[Preset], Preset], optional):
                Preset used to fill idx, a_src, a_src_cut, a_enc_cut and chapter attributes.
                Defaults to NoPreset.

            workdir (AnyPath, optional):
                Work directory. Default to the current directorie where the script is launched.
        """
        self.workdir = VPath(workdir)


        self.path = VPath(path)
        self.path_without_ext = self.path.with_suffix('')
        self.work_filename = self.path.stem

        self.idx = idx

        self.name = VPath(sys.argv[0]).stem


        self.a_src, self.a_src_cut, self.a_enc_cut, self.chapter = (None, ) * 4
        if isinstance(preset, Preset):
            self.preset = [preset]
        else:
            self.preset = sorted(preset, key=attrgetter('preset_type'))
        for p in self.preset:
            self._fill_preset(p)


        if self.idx:
            self.clip = self.idx(str(path))
            self.trims_or_dfs = trims_or_dfs

            self.name_clip_output = VPath(self.name + '.265')
            self.name_file_final = VPath(self.name + '.mkv')

            self.name_clip_output_lossless = VPath(self.name + '_lossless.mkv')
            self.do_lossless = False

            self.qpfile = VPath(self.name + '_qpfile.log')
            self.do_qpfile = False

        super().__init__()

    def __str__(self) -> str:
        self.preset = [vars(p) for p in self.preset]  # type: ignore
        return pformat(vars(self), width=100, sort_dicts=False)

    def _fill_preset(self, p: Preset) -> None:
        if self.idx is None:
            self.idx = p.idx

        if self.a_src is None and p.a_src is not None:
            if p.a_src == VPath():
                self.a_src = VPath()
            else:
                self.a_src = self.workdir / p.a_src.format(work_filename=self.work_filename, num='{}')

        if self.a_src_cut is None and p.a_src_cut is not None:
            if p.a_src_cut == VPath():
                self.a_src_cut = VPath()
            else:
                self.a_src_cut = self.workdir / p.a_src_cut.format(work_filename=self.work_filename, num='{}')

        if self.a_enc_cut is None and p.a_enc_cut is not None:
            if p.a_enc_cut == VPath():
                self.a_enc_cut = VPath()
            else:
                self.a_enc_cut = self.workdir / p.a_enc_cut.format(work_filename=self.work_filename, num='{}')

        if self.chapter is None and p.chapter is not None:
            self.chapter = self.workdir / p.chapter.format(name=self.name)

    @property
    def trims_or_dfs(self) -> Union[List[Union[Trim, DF]], Trim, None]:
        return self._trims_or_dfs

    @trims_or_dfs.setter
    def trims_or_dfs(self, x: Union[List[Union[Trim, DF]], Trim, None]) -> None:
        self._trims_or_dfs = x
        if x:
            self.clip_cut = adjust_clip_frames(self.clip, x if isinstance(x, list) else [x])
        else:
            self.clip_cut = self.clip

    @property
    def media_info(self) -> MediaInfo:
        return cast(MediaInfo, MediaInfo.parse(self.path))
