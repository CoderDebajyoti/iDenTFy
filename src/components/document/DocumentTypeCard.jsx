import React from 'react';
import { BookMarked, CreditCard, Building2, Car, Check } from 'lucide-react';

const DOC_TYPES = [
  {
    id: 'passport',
    title: 'Passport',
    icon: BookMarked,
    desc: 'Republic of India Passport (P) or ICAO 9303 international travel document.',
  },
  {
    id: 'id_card',
    title: 'Identity Card',
    icon: CreditCard,
    desc: 'Indian National Identity (Aadhaar / Voter ID / Citizen Identity card).',
  },
  {
    id: 'residence_permit',
    title: 'Residence / Visa',
    icon: Building2,
    desc: 'OCI Card, Foreigner Registration (FRRO) or Indian e-Visa for arrivals.',
  },
  {
    id: 'driver_license',
    title: 'Driver License',
    icon: Car,
    desc: 'Indian Motor Vehicle Driving Licence (Sarathi / MoRTH national standard).',
  },
];

export default function DocumentTypeCard({ selected, onSelect }) {
  return (
    <div className="document-type-grid" role="radiogroup" aria-label="Select Document Type">
      {DOC_TYPES.map((doc) => {
        const Icon = doc.icon;
        const isSelected = selected === doc.id;

        return (
          <div
            key={doc.id}
            role="radio"
            aria-checked={isSelected}
            tabIndex={0}
            className={`doc-type-card ${isSelected ? 'selected' : ''}`}
            onClick={() => onSelect(doc.id)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onSelect(doc.id);
              }
            }}
          >
            <div className="doc-type-top">
              <div className="doc-icon-wrapper">
                <Icon size={22} />
              </div>
              <div className="doc-radio-check">
                {isSelected && <Check size={13} strokeWidth={3} />}
              </div>
            </div>

            <div>
              <div className="doc-type-title">{doc.title}</div>
              <div className="doc-type-desc">{doc.desc}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
