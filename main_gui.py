#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minecraft Bot Client - GUI Version Entry Point"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.gui_main import run_gui

if __name__ == "__main__":
    run_gui()
