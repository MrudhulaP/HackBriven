import React, { createContext, useContext, useState, useEffect } from 'react';
import { Language } from '../types';

interface Translations {
  appName: string;
  tagline: string;
  namaste: string;
  subGreeting: string;
  totalOutstanding: string;
  todayCredit: string;
  todayCollections: string;
  totalCustomers: string;
  talkToBolKhata: string;
  talkSubtitle: string;
  tapAndSpeak: string;
  listening: string;
  processing: string;
  confirmTransactions: string;
  editTranscript: string;
  cancel: string;
  confirm: string;
  dashboard: string;
  voiceAssistant: string;
  customers: string;
  transactions: string;
  reports: string;
  reminders: string;
  settings: string;
  addCredit: string;
  recordPayment: string;
  addCustomer: string;
  viewLedger: string;
  recentTransactions: string;
  credit: string;
  payment: string;
  balance: string;
  today: string;
  yesterday: string;
  status: string;
  amount: string;
  actions: string;
  searchCustomers: string;
  noTransactions: string;
  offlineNotice: string;
  demoModeNotice: string;
}

const DICTIONARY: Record<Language, Translations> = {
  hi: {
    appName: "बोलखाता",
    tagline: "The Ledger You Talk To.",
    namaste: "नमस्ते",
    subGreeting: "आज आपकी दुकान का पूरा हिसाब यहाँ है।",
    totalOutstanding: "कुल बाकी उधार",
    todayCredit: "आज दिया उधार",
    todayCollections: "आज की वसूली",
    totalCustomers: "कुल ग्राहक",
    talkToBolKhata: "बोलखाता से बात करें",
    talkSubtitle: "बस बोलिए। आपके खाते का हिसाब मैं रखूँगा।",
    tapAndSpeak: "दबाएं और बोलें",
    listening: "सुन रहा हूँ... बोलिए",
    processing: "हिसाब समझा जा रहा है...",
    confirmTransactions: "क्या यह हिसाब सही है?",
    editTranscript: "लिखा हुआ बदलें",
    cancel: "रद्द करें",
    confirm: "खाते में दर्ज करें",
    dashboard: "डैशबोर्ड",
    voiceAssistant: "आवाज़ सहायक",
    customers: "ग्राहक",
    transactions: "लेन-देन",
    reports: "रिपोर्ट्स",
    reminders: "तगादा (याद दिलाएं)",
    settings: "सेटिंग्स",
    addCredit: "उधार दें",
    recordPayment: "जमा दर्ज करें",
    addCustomer: "नया ग्राहक",
    viewLedger: "खाता देखें",
    recentTransactions: "हाल के लेन-देन",
    credit: "उधार (+)",
    payment: "जमा (-)",
    balance: "बाकी",
    today: "आज",
    yesterday: "कल",
    status: "स्थिति",
    amount: "रुपये",
    actions: "कार्रवाई",
    searchCustomers: "ग्राहक का नाम या मोबाइल खोजें...",
    noTransactions: "अभी कोई लेन-देन दर्ज नहीं है।",
    offlineNotice: "ऑफ़लाइन मोड: लेन-देन स्थानीय रूप से सुरक्षित हैं। इंटरनेट आने पर सिंक होंगे।",
    demoModeNotice: "डेमो मोड सक्रिय है (शर्मा किराना एवं जनरल स्टोर)"
  },
  kn: {
    appName: "ಬೋಲ್‌ಖಾತಾ",
    tagline: "The Ledger You Talk To.",
    namaste: "ನಮಸ್ಕಾರ",
    subGreeting: "ಇಂದು ನಿಮ್ಮ ಅಂಗಡಿಯ ಸಂಪೂರ್ಣ ಲೆಕ್ಕ ಇಲ್ಲಿದೆ.",
    totalOutstanding: "ಒಟ್ಟು ಬಾಕಿ ಸಾಲ",
    todayCredit: "ಇಂದು ಕೊಟ್ಟ ಸಾಲ",
    todayCollections: "ಇಂದಿನ ವಸೂಲಿ",
    totalCustomers: "ಒಟ್ಟು ಗ್ರಾಹಕರು",
    talkToBolKhata: "ಬೋಲ್‌ಖಾತಾ ಜೊತೆ ಮಾತನಾಡಿ",
    talkSubtitle: "ಕೇವಲ ಮಾತನಾಡಿ. ನಿಮ್ಮ ಲೆಕ್ಕವನ್ನು ನಾನು ನೋಡಿಕೊಳ್ಳುತ್ತೇನೆ.",
    tapAndSpeak: "ಒತ್ತಿ ಮಾತನಾಡಿ",
    listening: "ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದ್ದೇನೆ... ಮಾತನಾಡಿ",
    processing: "ಲೆಕ್ಕ ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ...",
    confirmTransactions: "ಈ ಲೆಕ್ಕ ಸರಿಯಾಗಿದೆಯೇ?",
    editTranscript: "ಪಠ್ಯ ತಿದ್ದಿ",
    cancel: "ರದ್ದುಮಾಡಿ",
    confirm: "ಖಾತೆಗೆ ಸೇರಿಸಿ",
    dashboard: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    voiceAssistant: "ಧ್ವನಿ ಸಹಾಯಕ",
    customers: "ಗ್ರಾಹಕರು",
    transactions: "ವ್ಯವಹಾರಗಳು",
    reports: "ವರದಿಗಳು",
    reminders: "ಜ್ಞಾಪನೆಗಳು",
    settings: "ಸೆಟ್ಟಿಂಗ್ಸ್",
    addCredit: "ಸಾಲ ನೀಡಿ",
    recordPayment: "ಪಾವತಿ ದಾಖಲಿಸಿ",
    addCustomer: "ಹೊಸ ಗ್ರಾಹಕ",
    viewLedger: "ಖಾತೆ ವೀಕ್ಷಿಸಿ",
    recentTransactions: "ಇತ್ತೀಚಿನ ವ್ಯವಹಾರಗಳು",
    credit: "ಸಾಲ (+)",
    payment: "ಪಾವತಿ (-)",
    balance: "ಬಾಕಿ",
    today: "ಇಂದು",
    yesterday: "ನಿನ್ನೆ",
    status: "ಸ್ಥಿತಿ",
    amount: "ಮೊತ್ತ",
    actions: "ಕ್ರಮ",
    searchCustomers: "ಗ್ರಾಹಕರ ಹೆಸರು ಅಥವಾ ಮೊಬೈಲ್ ಹುಡುಕಿ...",
    noTransactions: "ಇನ್ನೂ ಯಾವುದೇ ವ್ಯವಹಾರಗಳಿಲ್ಲ.",
    offlineNotice: "ಆಫ್‌ಲೈನ್ ಮೋಡ್: ವ್ಯವಹಾರಗಳು ಸಾಧನದಲ್ಲಿ ಉಳಿದಿವೆ. ಆನ್‌ಲೈನ್‌ಗೆ ಬಂದಾಗ ಸಿಂಕ್ ಆಗುತ್ತವೆ.",
    demoModeNotice: "ಡೆಮೊ ಮೋಡ್ ಸಕ್ರಿಯವಾಗಿದೆ (ಶರ್ಮಾ ಕಿರಾಣಿ ಅಂಗಡಿ)"
  },
  en: {
    appName: "BolKhata",
    tagline: "The Ledger You Talk To.",
    namaste: "Namaste",
    subGreeting: "Here's what's happening in your shop today.",
    totalOutstanding: "Total Outstanding",
    todayCredit: "Today's Credit",
    todayCollections: "Today's Collections",
    totalCustomers: "Total Customers",
    talkToBolKhata: "Talk to BolKhata",
    talkSubtitle: "Just speak. I'll take care of your ledger.",
    tapAndSpeak: "Tap and Speak",
    listening: "Listening... speak now",
    processing: "Understanding transaction...",
    confirmTransactions: "Here's what I understood",
    editTranscript: "Edit Transcript",
    cancel: "Cancel",
    confirm: "Confirm & Save",
    dashboard: "Dashboard",
    voiceAssistant: "Voice Assistant",
    customers: "Customers",
    transactions: "Transactions",
    reports: "Reports",
    reminders: "Reminders",
    settings: "Settings",
    addCredit: "Add Credit",
    recordPayment: "Record Payment",
    addCustomer: "Add Customer",
    viewLedger: "View Ledger",
    recentTransactions: "Recent Transactions",
    credit: "Credit (+)",
    payment: "Payment (-)",
    balance: "Balance",
    today: "Today",
    yesterday: "Yesterday",
    status: "Status",
    amount: "Amount",
    actions: "Actions",
    searchCustomers: "Search customers by name or mobile...",
    noTransactions: "No transactions recorded yet.",
    offlineNotice: "Offline mode: Transactions are saved locally and will sync when reconnected.",
    demoModeNotice: "Demo mode active (Sharma Kirana & General Store)"
  }
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
  languagesList: { code: Language; label: string; native: string }[];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    return (localStorage.getItem('bolkhata_lang') as Language) || 'hi';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('bolkhata_lang', lang);
  };

  const languagesList = [
    { code: 'hi' as Language, label: 'Hindi', native: 'हिंदी' },
    { code: 'kn' as Language, label: 'Kannada', native: 'ಕನ್ನಡ' },
    { code: 'en' as Language, label: 'English', native: 'English' },
  ];

  const t = DICTIONARY[language] || DICTIONARY.en;

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, languagesList }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
