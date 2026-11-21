import React, { useState, useRef } from 'react';
import { api } from '../services/api';
import { ReceiptScanResult } from '../types';
import {
  Camera,
  Upload,
  CheckCircle,
  AlertCircle,
  X,
  FileText,
  DollarSign,
  Calendar,
  Sparkles,
  ArrowUpRight,
  ArrowDownLeft,
  Loader2
} from 'lucide-react';
import confetti from 'canvas-confetti';

interface ReceiptScannerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onReceiptConfirmed?: () => void;
}

export const ReceiptScannerModal: React.FC<ReceiptScannerModalProps> = ({
  isOpen,
  onClose,
  onReceiptConfirmed
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<ReceiptScanResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string>('');

  // Editable fields after extraction
  const [vendorName, setVendorName] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [txDate, setTxDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [txType, setTxType] = useState<'CREDIT' | 'PAYMENT'>('CREDIT');
  const [notes, setNotes] = useState<string>('Paper bill scan');

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileSelect = async (selectedFile: File) => {
    setErrorMsg('');
    setSuccessMsg('');
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setIsScanning(true);

    try {
      const result = await api.scanReceipt(selectedFile);
      setScanResult(result);
      setVendorName(result.vendor_name || 'Vendor');
      setAmount(result.total_amount ? result.total_amount.toString() : '0');
      if (result.date) setTxDate(result.date);
      setNotes(`Scanned Bill (${result.items?.length || 0} items)`);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to scan receipt image');
    } finally {
      setIsScanning(false);
    }
  };

  // Demo sample receipt when user wants to test quickly without camera
  const handleUseDemoReceipt = async () => {
    setErrorMsg('');
    setIsScanning(true);
    // Create a mock canvas image
    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 300;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, 400, 300);
      ctx.fillStyle = '#000000';
      ctx.font = 'bold 20px sans-serif';
      ctx.fillText('Sri Lakshmi Wholesalers', 40, 50);
      ctx.font = '14px sans-serif';
      ctx.fillText('Atta 10kg - Rs. 420', 40, 90);
      ctx.fillText('Mustard Oil 1L - Rs. 180', 40, 120);
      ctx.fillText('Sugar 5kg - Rs. 220', 40, 150);
      ctx.font = 'bold 18px sans-serif';
      ctx.fillText('Total: Rs. 820.00', 40, 200);
      ctx.fillText('Date: 2026-11-21', 40, 230);
    }

    canvas.toBlob(async (blob) => {
      if (blob) {
        const dummyFile = new File([blob], 'demo_kirana_receipt.png', { type: 'image/png' });
        await handleFileSelect(dummyFile);
      }
    }, 'image/png');
  };

  const handleConfirmReceipt = async () => {
    if (!vendorName.trim()) {
      setErrorMsg('Please specify vendor or customer name');
      return;
    }
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      setErrorMsg('Please enter a valid amount greater than ₹0');
      return;
    }

    setIsSaving(true);
    setErrorMsg('');

    try {
      const res = await api.confirmReceipt({
        vendor_or_customer_name: vendorName.trim(),
        amount: numAmount,
        type: txType,
        transaction_date: txDate,
        description: notes
      });

      setSuccessMsg(res.message || 'Successfully recorded to ledger!');
      confetti({
        particleCount: 70,
        spread: 60,
        origin: { y: 0.6 },
        colors: ['#1B4332', '#40916C', '#F4A261', '#52B788']
      });

      setTimeout(() => {
        if (onReceiptConfirmed) onReceiptConfirmed();
        onClose();
      }, 1200);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to confirm receipt entry');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/60 backdrop-blur-xs animate-in fade-in overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-cream-200 space-y-4 my-8">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-cream-200 pb-3">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-forest-100 text-forest-800 flex items-center justify-center">
              <Camera className="w-5 h-5 text-forest-700" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-forest-900 leading-tight">
                Bill & Receipt Scanner
              </h3>
              <p className="text-2xs text-charcoal-500 font-medium">
                OCR & Voice-Activated Paper Invoice Reader
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-500 hover:bg-cream-100 hover:text-charcoal-900 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Capture / Upload Buttons */}
        {!previewUrl ? (
          <div className="space-y-3 py-4">
            <div className="border-2 border-dashed border-cream-300 rounded-2xl p-6 text-center space-y-3 bg-cream-50/50">
              <div className="flex justify-center gap-3">
                <button
                  type="button"
                  onClick={() => cameraInputRef.current?.click()}
                  className="px-4 py-2.5 bg-forest-800 hover:bg-forest-900 text-white rounded-xl text-xs font-bold shadow-xs flex items-center gap-2"
                >
                  <Camera className="w-4 h-4" />
                  <span>Take Photo</span>
                </button>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2.5 bg-white border border-cream-300 hover:bg-cream-100 text-charcoal-800 rounded-xl text-xs font-bold shadow-2xs flex items-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload File</span>
                </button>
              </div>

              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files?.[0]) handleFileSelect(e.target.files[0]);
                }}
              />
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files?.[0]) handleFileSelect(e.target.files[0]);
                }}
              />

              <p className="text-2xs text-charcoal-500 font-medium">
                Supports photos of paper bills, wholesaler receipts, and handwritten slips.
              </p>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={handleUseDemoReceipt}
                className="inline-flex items-center gap-1.5 text-2xs font-bold text-forest-800 bg-forest-50 px-3 py-1.5 rounded-lg border border-forest-200 hover:bg-forest-100"
              >
                <Sparkles className="w-3.5 h-3.5 text-amberGold-600" />
                <span>Test with Demo Kirana Receipt</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Image Preview & Scan status */}
            <div className="relative rounded-2xl overflow-hidden border border-cream-200 max-h-48 bg-charcoal-900 flex items-center justify-center">
              <img
                src={previewUrl}
                alt="Receipt preview"
                className="max-h-48 w-auto object-contain"
              />
              {isScanning && (
                <div className="absolute inset-0 bg-charcoal-900/70 flex flex-col items-center justify-center text-white gap-2">
                  <Loader2 className="w-6 h-6 animate-spin text-amberGold-500" />
                  <span className="text-xs font-bold tracking-wide">
                    Extracting vendor, amount & items...
                  </span>
                </div>
              )}
              <button
                type="button"
                onClick={() => {
                  setPreviewUrl(null);
                  setScanResult(null);
                  setFile(null);
                }}
                className="absolute top-2 right-2 p-1 bg-black/60 text-white rounded-lg hover:bg-black/80"
                title="Retake photo"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Verification Form */}
            {!isScanning && (
              <div className="space-y-3 bg-cream-50 p-4 rounded-2xl border border-cream-200">
                <div className="flex items-center justify-between">
                  <span className="text-2xs font-extrabold uppercase tracking-wider text-forest-800">
                    Verify Extracted Details
                  </span>
                  <span className="text-3xs font-bold bg-forest-100 text-forest-800 px-2 py-0.5 rounded">
                    Confidence: {Math.round((scanResult?.confidence || 0.85) * 100)}%
                  </span>
                </div>

                {/* Vendor / Customer Name */}
                <div>
                  <label className="text-2xs font-bold text-charcoal-700 block mb-1">
                    Vendor / Customer Name *
                  </label>
                  <input
                    type="text"
                    value={vendorName}
                    onChange={(e) => setVendorName(e.target.value)}
                    placeholder="e.g. Sri Lakshmi Wholesalers / Ramesh"
                    className="w-full text-xs font-bold px-3 py-2 bg-white border border-cream-300 rounded-xl text-charcoal-900 focus:ring-2 focus:ring-forest-600 outline-none"
                  />
                </div>

                {/* Amount & Date */}
                <div className="grid grid-cols-2 gap-2.5">
                  <div>
                    <label className="text-2xs font-bold text-charcoal-700 block mb-1">
                      Total Amount (₹) *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      className="w-full text-base font-black px-3 py-1.5 bg-white border border-cream-300 rounded-xl text-forest-900 focus:ring-2 focus:ring-forest-600 outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-2xs font-bold text-charcoal-700 block mb-1">
                      Invoice Date
                    </label>
                    <input
                      type="date"
                      value={txDate}
                      onChange={(e) => setTxDate(e.target.value)}
                      className="w-full text-xs font-semibold px-3 py-2 bg-white border border-cream-300 rounded-xl text-charcoal-800 focus:ring-2 focus:ring-forest-600 outline-none"
                    />
                  </div>
                </div>

                {/* Transaction Type Selector */}
                <div>
                  <label className="text-2xs font-bold text-charcoal-700 block mb-1">
                    Transaction Type in Ledger
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setTxType('CREDIT')}
                      className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 border transition-all ${
                        txType === 'CREDIT'
                          ? 'bg-forest-800 text-white border-forest-900 shadow-2xs'
                          : 'bg-white text-charcoal-700 border-cream-300 hover:bg-cream-100'
                      }`}
                    >
                      <ArrowUpRight className="w-3.5 h-3.5" />
                      <span>Credit (Udhaar) +</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setTxType('PAYMENT')}
                      className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 border transition-all ${
                        txType === 'PAYMENT'
                          ? 'bg-amberGold-600 text-white border-amberGold-700 shadow-2xs'
                          : 'bg-white text-charcoal-700 border-cream-300 hover:bg-cream-100'
                      }`}
                    >
                      <ArrowDownLeft className="w-3.5 h-3.5" />
                      <span>Payment (Jama) -</span>
                    </button>
                  </div>
                </div>

                {/* Line Items Preview if any */}
                {scanResult?.items && scanResult.items.length > 0 && (
                  <div className="pt-2 border-t border-cream-200">
                    <p className="text-3xs font-bold text-charcoal-600 uppercase mb-1">
                      Detected Items ({scanResult.items.length})
                    </p>
                    <div className="max-h-24 overflow-y-auto space-y-1">
                      {scanResult.items.map((it, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between text-2xs text-charcoal-700 bg-white px-2 py-1 rounded-lg border border-cream-200"
                        >
                          <span className="truncate">{it.name}</span>
                          <span className="font-bold text-forest-800 shrink-0">
                            ₹{it.price || '--'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Status Messages */}
        {errorMsg && (
          <div className="p-3 rounded-xl bg-terracotta-50 border border-terracotta-200 text-terracotta-800 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div className="p-3 rounded-xl bg-forest-50 border border-forest-200 text-forest-800 text-xs font-bold flex items-center gap-2">
            <CheckCircle className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Footer actions */}
        <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-cream-200">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-bold text-charcoal-600 hover:bg-cream-100 rounded-xl"
          >
            Cancel
          </button>
          {previewUrl && !isScanning && (
            <button
              type="button"
              disabled={isSaving}
              onClick={handleConfirmReceipt}
              className="px-5 py-2.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold rounded-xl shadow-xs flex items-center gap-2"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Writing to Ledger...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Confirm & Save to Ledger</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
