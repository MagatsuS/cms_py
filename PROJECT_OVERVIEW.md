# CMS_PY - Digital Signage Content Management System

## Project Overview

CMS_PY is a Python-based Digital Signage Content Management System designed for managing TV screens and digital displays via Raspberry Pi players. This project is inspired by and aims to be compatible with the Laravel-based cms_dupe system.

## Purpose

This system enables organizations to:
- Upload and manage media content (images, videos, HTML)
- Create playlists and schedules
- Deploy content to Raspberry Pi players controlling TV screens
- Monitor player status in real-time
- Manage multiple locations and screen groups

## Target Use Cases

- **Retail Chains**: Menu boards, promotions, sales announcements
- **Corporate Communications**: Internal announcements, dashboards, metrics
- **Digital Billboards**: Advertising campaigns with scheduling
- **Information Displays**: Airport info, transit displays, wayfinding
- **Event Management**: Dynamic displays for conferences and festivals
- **Hospitality**: Hotel lobby displays, restaurant menus

## Core Workflow

1. **Upload** - Media files to cloud storage (DigitalOcean Spaces)
2. **Manage** - Organize content into playlists, groups, and schedules
3. **Deploy** - Push content to Raspberry Pi players controlling TV screens

## Technology Stack

### Backend (Target)
- **Framework**: Django/FastAPI (Python 3.10+)
- **Database**: PostgreSQL/MySQL
- **API**: RESTful API compatible with cms_dupe
- **File Storage**: DigitalOcean Spaces (S3-compatible)
- **Authentication**: JWT/Token-based auth
- **Real-time**: WebSocket integration (compatible with Laravel Reverb)

### Raspberry Pi Player
- **Language**: Python 3.x
- **Display**: Full-screen kiosk mode
- **Video**: Hardware accelerated playback
- **Integration**: HDMI-CEC (TV power control), GPIO
- **Communication**: REST API + WebSocket
- **Updates**: OTA (Over-the-air) updates

## Key Features (Planned)

### Content Management
- Media asset upload and organization
- Asset validity periods
- Cloud storage integration
- Thumbnail generation
- Asset categorization

### Playlist System
- Playlist creation and management
- Drag-and-drop ordering
- Asset duration configuration
- Multiple layout support
- Default playlist assignment

### Display Layouts
- Multi-zone layout builder
- HD and Full HD support
- Portrait/landscape orientation
- Zone-based asset assignment
- Custom layout templates

### Player Management
- Player registration (QR code + manual)
- Real-time status monitoring
- Remote configuration
- Screenshot capture
- Location tracking
- Player grouping

### Scheduling System
- Date-range scheduling
- Time-window scheduling
- Priority-based ordering
- Default playlist fallback
- Advanced calendar integration

### Deployment System
- One-click deployment
- Group-based batch deployment
- Background progress tracking
- Seamless content transition
- Offline content caching

### Analytics & Reporting
- Player statistics dashboard
- Deployment history
- Asset usage analytics
- Activity logs (audit trail)
- CSV/Excel export

### User Management
- Role-based access control (RBAC)
- Multi-tier user hierarchy
- Activity logging
- Password management
- User permissions

### Subscription & Licensing
- Tiered subscription plans
- License key management
- Payment integration
- Usage limit enforcement

## Database Models (Planned)

### Core Models
- **Asset** - Media files
- **Playlist** - Content playlists
- **PlaylistAsset** - Playlist-asset relationships
- **Group** - Player groups
- **Schedule** - Scheduling rules
- **Layout** - Display layouts
- **LayoutZone** - Layout zones
- **Player** - Registered devices
- **Deployment** - Deployment records
- **User** - User accounts
- **Role** - User roles
- **Permission** - Permissions
- **License** - Player licenses
- **Subscription** - User subscriptions
- **Campaign** - Marketing campaigns
- **ActivityLog** - Audit trail

## API Compatibility

This project aims to maintain API compatibility with the cms_dupe Laravel system to ensure:
- Raspberry Pi players can work with both systems
- Smooth migration path
- Shared infrastructure (storage, database)
- Consistent authentication

## Project Structure (Target)

```
cms_py/
├── app/
│   ├── api/              # API endpoints
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── controllers/      # Request handlers
│   ├── middleware/       # Authentication, logging
│   └── utils/            # Helper functions
├── config/               # Configuration files
├── database/
│   ├── migrations/       # Database migrations
│   └── seeders/          # Data seeders
├── tests/                # Unit and integration tests
├── storage/              # File storage
├── raspberry-pi-player/  # Raspberry Pi client (Python)
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
└── README.md
```

## Development Status

**Status**: Initial Development

This project is currently being set up and will progressively implement features from the cms_dupe reference system.

## Development Phases

### Phase 1: Foundation
- Project structure setup
- Database models
- Basic CRUD operations
- Authentication system

### Phase 2: Core Features
- Asset management
- Playlist system
- Player registration
- Basic deployment

### Phase 3: Advanced Features
- Scheduling system
- Layout builder
- Real-time updates
- Analytics

### Phase 4: Integration
- Payment gateway
- Subscription system
- Offline sync
- HDMI-CEC control

## Configuration

### Environment Variables Required
- **Database**: Connection details
- **Storage**: DigitalOcean Spaces credentials
- **API**: Secret keys, URLs
- **Payment**: Gateway credentials (optional)
- **WebSocket**: Real-time update settings

## Getting Started

(To be added as development progresses)

## Documentation

- See cms_dupe project at `C:\laragon\www\cms_dupe` for reference implementation
- API documentation: (To be added)
- Player setup guide: (To be added)

## Contributing

(To be added)

## License

(To be determined)

---

**Project Status**: In Development
**Last Updated**: 2025-11-24
**Reference Project**: cms_dupe (Laravel)
