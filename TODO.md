agentic-robotic-arm/
│
├── README.md
├── requirements.txt
├── setup.md
│
├── docs/
│ ├── architecture/
│ │ ├── system_architecture.png
│ │ ├── agent_flow_diagram.png
│ │ └── hardware_block_diagram.png
│ │
│ ├── research/
│ │ ├── literature_review.md
│ │ ├── paper_summaries.md
│ │ ├── comparison_tables.md
│ │ └── references.md
│ │
│ ├── reports/
│ │ ├── final_report.docx
│ │ └── ppt_slides.pptx
│ │
│ └── demo/
│ ├── images/
│ └── videos/
│
├── agents/
│ ├── **init**.py
│ ├── master_agent.py
│ ├── speech_agent.py
│ ├── vision_agent.py
│ ├── context_agent.py
│ └── safety_agent.py
│
├── planner/
│ ├── **init**.py
│ ├── task_planner.py
│ └── motion_sequences.py
│
├── hardware/
│ ├── **init**.py
│ ├── servo_controller.py
│ ├── gpio_interface.py
│ ├── power_manager.py
│ └── camera_interface.py
│
├── simulation/
│ ├── **init**.py
│ ├── mock_servo.py
│ ├── mock_gpio.py
│ └── test_environment.py
│
├── perception/
│ ├── **init**.py
│ ├── speech/
│ │ ├── speech_recognizer.py
│ │ └── command_parser.py
│ │
│ └── vision/
│ ├── camera_stream.py
│ ├── object_detector.py
│ └── vision_utils.py
│
├── config/
│ ├── robot_config.yaml
│ ├── servo_limits.yaml
│ ├── agent_settings.yaml
│ └── system_modes.yaml
│
├── logs/
│ ├── system.log
│ ├── agent.log
│ └── error.log
│
├── scripts/
│ ├── start_system.py
│ ├── calibrate_servos.py
│ ├── test_microphone.py
│ └── test_camera.py
│
├── tests/
│ ├── test_agents.py
│ ├── test_planner.py
│ └── test_hardware_interface.py
│
└── utils/
├── logger.py
├── helpers.py
└── constants.py
