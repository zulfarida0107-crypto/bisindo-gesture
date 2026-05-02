# rule base:
# "touch" = mendeteksi tangan dengan adanya sentuhan 
# "none" = tidak mendeteksi tangan
# "shape" = mendeteksi tangan dengan derajat
# trigger = 'true' untuk jari menekuk/melengkung dan 'false' untuk jari lurus

BISINDO_RULES = {
    "A": {
        "right_hand": { "mode": "touch" },
        "left_hand": { "mode": "touch" },
        "inter_touch": [
            {
                "right": [
                    {"finger": "Index", "phalange": "distal"},
                    {"finger": "Thumb", "phalange": "distal"}
                ],
                "left": [
                    {"finger": "Index", "phalange": "distal"},
                    {"finger": "Thumb", "phalange": "distal"}
                ]
            }
        ]
    },

    "B": {
        "right_hand": { "mode": "touch" },
        "left_hand": { "mode": "touch" },
        "inter_touch": [
            {
                "right": [
                    {"finger": "Index", "phalange": "distal"},
                    {"finger": "Index", "phalange": "intermediate"},
                    {"finger": "Index", "phalange": "proximal"}
                ],
                "left": [
                    {"finger": "Index", "phalange": "distal"},
                    {"finger": "Middle", "phalange": "distal"},
                    {"finger": "Ring", "phalange": "distal"}
                ]
            }
        ]
    },

    "C": {
        "right_hand": {
            "mode": "shape",
            "is_curved": False,
            "target_fingers": ["Thumb", "Index"],
            "angle_range": [270, 90]
        },
        "left_hand": {
            "mode": "none"
        },
        "inter_touch": []
    },

    "D": {
        "right_hand": {
            "mode": "touch"
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": False,
            "target_fingers": ["Index"],
            "angle_range": [350, 10]
        },
        "inter_touch": [
            {
                "right": [
                    { "finger": "Index", "phalange": "distal" },
                    { "finger": "Thumb", "phalange": "distal" }
                ],
                "left": [
                    { "finger": "Index", "phalange": "distal" },
                    { "finger": "Index", "phalange": "proximal" }
                ]
            }
        ]
    },

    # EROR
    "E": {
        "right_hand": {
            "mode": "none"
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Index", "Middle", "Ring"],
            "angle_range": [0, 360]
        },
        "inter_touch": []
    },

    # EROR
    "F": {
        "right_hand": {
            "mode": "touch"
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Middle", "Ring", "Pinky"],
            "angle_range": [0, 360]
        },
        "inter_touch": [
            {
                "right": [
                    {"finger": "Index", "phalange": "distal"},
                    {"finger": "Thumb", "phalange": "distal"}
                ],
                "left": [
                    {"finger": "Index", "phalange": "distal"},
                    {"finger": "Thumb", "phalange": "distal"}
                ]
            }
        ]
    },

    # EROR
    "G": {
        "right_hand": {
            "mode": "shape",
            "is_curved": False,
            "target_fingers": ["Index"],
            "angle_range": [0, 360]
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Thumb", "Middle", "Ring", "Pinky"],
            "angle_range": [0, 360]
        },
        "inter_touch": []
    },

    # EROR
    "H": {
        "right_hand": { "mode": "touch" },
        "left_hand": { "mode": "touch" },
        "inter_touch": [
            {
                "right": [
                    {"finger": "Index", "phalange": "intermediate"}
                ],
                "left": [
                    {"finger": "Middle", "phalange": "distal"},
                ]
            }
        ]
    },

    # EROR
    # KHUSUS "shape"
    "I": {
        "right_hand": {
            "mode": "none"
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": False,
            "target_fingers": ["Pinky"],
            "angle_range": [355, 0],
            "angle_reference": {
                "up": 0,
                "right": 90,
                "down": 180,
                "left": 270,
                "full": 360
            }
        },
        # touch tidak digunakan
        "inter_touch": []
    },

    # EROR  
    # KHUSUS "shape"
    "J": {
        "right_hand": { "mode": "none" },
        "left_hand": {
            "mode": "shape",
            "is_curved": False,
            "target_fingers": ["Pinky"],
            "angle_range": [180, 270]
        },
        "inter_touch": []
    },

    "K": {
        "right_hand": {
            "mode": "shape",
            "is_curved": False,
            "target_fingers": ["Index", "Middle"],
            "angle_range": [0, 360]
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Thumb", "Ring", "Pinky"],
            "angle_range": [0, 360]
        },
        "inter_touch": []
    },

    "L": {
        "right_hand": { "mode": "none" },
        "left_hand": {
            "mode": "shape",
            "is_curved": False,
            "target_fingers": ["Thumb", "Index"],
            "angle_range": [80, 100]
        },
        "inter_touch": []
    },

    "M": {
        "right_hand": { "mode": "none" },
        "left_hand": { "mode": "touch" },
        "inter_touch": [
            {
                "right": [],
                "left": [
                    {"finger": "Index", "phalange": "distal"},
                    {"finger": "Middle", "phalange": "distal"},
                    {"finger": "Ring", "phalange": "distal"}
                ]
            }
        ]
    },

    "N": {
        "right_hand": { "mode": "none" },
        "left_hand": { "mode": "touch" },
        "inter_touch": [
            {
                "right": [],
                "left": [
                    {"finger": "Index", "phalange": "distal"},
                    {"finger": "Middle", "phalange": "distal"}
                ]
            }
        ]
    },

    "O": {
        "right_hand": { "mode": "touch" },
        "left_hand": { "mode": "none" },

        "inter_touch": [
            {
                "right": [
                    { "finger": "Thumb", "phalange": "distal" },
                    { "finger": "Index", "phalange": "distal" }
                ],
                "left": []
            }
        ]
    },

    "P": {
        "right_hand": { "mode": "touch" },
        "left_hand": { "mode": "touch" },

        "inter_touch": [
            {
                "right": [
                    { "finger": "Thumb", "phalange": "distal" },
                    { "finger": "Index", "phalange": "distal" }
                ],
                "left": [
                    { "finger": "Index", "phalange": "distal" }
                ]
            }
        ]
    },

    "Q": {
        "right_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Thumb", "Index"],
            "angle_range": [0, 270],
            "angle_reference": {
                "up": 0,
                "right": 90,
                "down": 180,
                "left": 270,
                "full": 360
            }
        },
        "left_hand": {
            "mode": "touch",
        },
        # touch tidak digunakan
        "inter_touch": [
            {
                "left": [
                    {"finger": "Index", "phalange": "distal"}
                ],
            }
        ]
    },

    "R": {
        "right_hand": { "mode": "none" },
        "left_hand": { "mode": "shape" },
        "inter_touch": [
            {
                "right": [],
                "left": [
                    {"finger": "Thumb", "phalange": "distal"},
                    {"finger": "Index", "phalange": "distal"}
                ]
            }
        ]
    },

    "S": {
        "right_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Thumb", "Index"],
            "angle_range": [0, 180],
            "angle_reference": {
                "up": 0,
                "right": 90,
                "down": 180,
                "left": 270,
                "full": 360
            }
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Thumb", "Index"],
            "angle_range": [0, 90],
            "angle_reference": {
                "up": 0,
                "right": 90,
                "down": 180,
                "left": 270,
                "full": 360
            }
        },
        # touch tidak digunakan
        "inter_touch": []
    },

    "T": {
        "right_hand": { "mode": "touch" },
        "left_hand": { "mode": "touch" },
        "inter_touch": [
            {
                "right": [
                    {"finger": "Index", "phalange": "distal"}
                ],
                "left": [
                    {"finger": "Index", "phalange": "intermediate"}
                ]
            }
        ]
    },

    "U": {
        "right_hand": {
            "mode": "none",
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Thumb", "Index"],
            "angle_range": [0, 10],
            "angle_reference": {
                "up": 0,
                "right": 90,
                "down": 180,
                "left": 270,
                "full": 360
            }
        },
        # touch tidak digunakan
        "inter_touch": []
    },

    "V": {
        "right_hand": {
            "mode": "none"
        },
        "left_hand": {
            "mode": "shape",
            "is_curved": True,
            "target_fingers": ["Index", "Middle"],
            "angle_range": [340, 350],
            "angle_reference": {
                "up": 0,
                "right": 90,
                "down": 180,
                "left": 270,
                "full": 360
            }
        },
        # touch tidak digunakan
        "inter_touch": []
    },


    "W": {
        "right_hand": { "mode": "touch" },
        "left_hand": { "mode": "touch" },
        "inter_touch": [
            {
                "right": [
                    {"finger": "Thumb", "phalange": "distal"}
                ],
                "left": [
                    {"finger": "Thumb", "phalange": "distal"}
                ]
            }
        ]
    },

    "X": {
        "right_hand": { "mode": "touch" },
        "left_hand": { "mode": "touch" },
        "inter_touch": [
            {
                "right": [
                    {"finger": "Index", "phalange": "intermediate"}
                ],
                "left": [
                    {"finger": "Index", "phalange": "intermediate"}
                ]
            }
        ]
    },

    "Y": {
        "right_hand": {
            "mode": "shape"
        },
        "left_hand": {
            "mode": "shape"
        },
        "inter_touch": [
            {
                "right": [
                    {
                        "hand_part": "palm_center",
                        "touch": "webbing_index_thumb"
                    }
                ],
                "left": [
                    {
                        "finger": "Index",
                        "angle_range": [350, 5]
                    },
                    {
                        "finger": "Middle",
                        "angle_range": [340, 330]
                    }
                ]
            }
        ]
    },

    "Z": {
    "right_hand": {
        "mode": "motion",
        "active_finger": "Index",
        "trajectory": "zigzag"
    },
    "left_hand": {
        "mode": "none"
    }
    }

}