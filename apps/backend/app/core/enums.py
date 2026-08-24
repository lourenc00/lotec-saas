import enum


class CompanyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    BLOCKED = "BLOCKED"
    INACTIVE = "INACTIVE"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INVITED = "INVITED"
    SUSPENDED = "SUSPENDED"
    DISABLED = "DISABLED"


class CompanyRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"
    ATTENDANT = "ATTENDANT"


class ServiceOrderStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    IN_ANALYSIS = "IN_ANALYSIS"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    WAITING_PART = "WAITING_PART"
    IN_REPAIR = "IN_REPAIR"
    READY = "READY"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"
    NO_REPAIR = "NO_REPAIR"


class SubscriptionStatus(str, enum.Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    SUSPENDED = "SUSPENDED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"
    CHARGED_BACK = "CHARGED_BACK"
    UNKNOWN = "UNKNOWN"


class DeviceCategory(str, enum.Enum):
    SMARTPHONE = "SMARTPHONE"
    TABLET = "TABLET"
    NOTEBOOK = "NOTEBOOK"
    COMPUTER = "COMPUTER"
    OTHER = "OTHER"


class FeatureValueType(str, enum.Enum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    STRING = "string"
