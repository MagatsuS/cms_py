from django.db import models
from django.utils import timezone
import uuid


class Player(models.Model):
    """Player model for Raspberry Pi devices"""

    # Player status
    ONLINE = 'online'
    OFFLINE = 'offline'
    PLAYING = 'playing'
    ERROR = 'error'

    STATUS_CHOICES = [
        (ONLINE, 'Online'),
        (OFFLINE, 'Offline'),
        (PLAYING, 'Playing'),
        (ERROR, 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='players')
    group = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='players')

    # Player identification
    name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=100, unique=True, db_index=True)
    registration_code = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Location
    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Hardware information
    hardware_model = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    player_version = models.CharField(max_length=20, blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)

    # Capabilities
    supports_hdmi_cec = models.BooleanField(default=False)
    supports_gpio = models.BooleanField(default=False)
    supports_offline = models.BooleanField(default=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OFFLINE)
    current_playlist = models.ForeignKey(
        'playlists.Playlist',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_players'
    )
    current_asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_players'
    )

    # Health monitoring
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    disk_usage = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    uptime = models.BigIntegerField(null=True, blank=True)  # Uptime in seconds

    # Network
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    mac_address = models.CharField(max_length=17, null=True, blank=True)

    # Licensing
    license = models.ForeignKey(
        'licenses.License',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='players'
    )
    is_licensed = models.BooleanField(default=False)
    license_expires_at = models.DateTimeField(null=True, blank=True)

    # Activity tracking
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    last_deployed_at = models.DateTimeField(null=True, blank=True)
    last_screenshot = models.CharField(max_length=500, null=True, blank=True)
    last_screenshot_at = models.DateTimeField(null=True, blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    auto_power_on = models.TimeField(null=True, blank=True)
    auto_power_off = models.TimeField(null=True, blank=True)
    orientation = models.CharField(max_length=20, default='landscape')
    volume = models.IntegerField(default=50)

    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete

    class Meta:
        db_table = 'players'
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['device_id']),
            models.Index(fields=['last_heartbeat']),
            models.Index(fields=['group']),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    @property
    def is_online(self):
        """Check if player is online based on last heartbeat"""
        if not self.last_heartbeat:
            return False

        from django.conf import settings
        threshold = timezone.now() - timezone.timedelta(
            seconds=settings.PLAYER_OFFLINE_THRESHOLD
        )
        return self.last_heartbeat > threshold

    @property
    def is_deleted(self):
        """Check if player is soft deleted"""
        return self.deleted_at is not None

    def update_heartbeat(self):
        """Update last heartbeat timestamp"""
        self.last_heartbeat = timezone.now()
        self.status = self.ONLINE if self.is_online else self.OFFLINE
        self.save(update_fields=['last_heartbeat', 'status'])

    def update_health(self, cpu=None, memory=None, disk=None, temp=None, uptime=None):
        """Update health monitoring data"""
        if cpu is not None:
            self.cpu_usage = cpu
        if memory is not None:
            self.memory_usage = memory
        if disk is not None:
            self.disk_usage = disk
        if temp is not None:
            self.temperature = temp
        if uptime is not None:
            self.uptime = uptime

        self.save(update_fields=['cpu_usage', 'memory_usage', 'disk_usage', 'temperature', 'uptime'])

    def soft_delete(self):
        """Soft delete the player"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        """Restore soft deleted player"""
        self.deleted_at = None
        self.is_active = True
        self.save()
