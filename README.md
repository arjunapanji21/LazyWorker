# Automatask - Web Data Entry Automation Tool

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A powerful and user-friendly GUI application for automating web-based data entry tasks. Built with Python, Selenium, and Tkinter.

## 🌟 Features

- **User-friendly GUI** for configuration and monitoring
- **Flexible field mapping** between Excel data and web forms
- **Multi-step form submission** support
- **Smart element detection** for login fields
- **Configurable actions** after form submission
- **Pause/Resume functionality** for better control
- **Progress tracking** with detailed status updates
- **Configuration save/load** for reusable automation tasks

## 📋 Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver matching your Chrome version

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Automatask.git
cd Automatask
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## 💻 Usage

1. Launch the application:
```bash
python main.py
```

2. Configure your automation:
   - Enter login URL and form URL
   - Provide login credentials
   - Select your Excel data file
   - Map Excel columns to web form fields
   - Configure post-submit actions

3. Run the automation:
   - Click "Start Automation"
   - Monitor progress in real-time
   - Use Pause/Resume if needed
   - Stop automation at any time

## 🔧 Configuration

### Field Mapping
- Map Excel columns to web elements using:
  - CSS Selectors
  - XPath
  - Element IDs

### Post-Submit Actions
Configure actions after form submission:
- Click buttons/links
- Input additional data
- Wait for elements
- Add delays between actions

## 📝 Example Configuration

```json
{
  "url": "https://example.com/login",
  "form_url": "https://example.com/form",
  "field_mappings": [
    {
      "excel_column": "Name",
      "selector_type": "ID",
      "web_selector": "name_field"
    }
  ],
  "post_submit_actions": [
    {
      "order": 1,
      "action": "click",
      "selector_type": "CSS",
      "selector": "button[type='submit']",
      "delay": 1
    }
  ]
}
```

## 🛠️ Technical Details

- **GUI**: Built with Tkinter for native look and feel
- **Web Automation**: Selenium WebDriver
- **Data Handling**: Pandas for Excel processing
- **Error Handling**: Robust error recovery and retry mechanisms
- **Configuration**: JSON-based config storage

## ⚡ Performance Features

- Smart element detection
- Optimized page load waiting
- Reduced CPU/memory usage
- Configurable timeouts
- Efficient Excel data processing

## 👤 Author

**Arjuna Panji Prakarsa**
- Website: [arjunaprakarsa.com](https://arjunaprakarsa.com)
- Version: 1.0.0

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request
